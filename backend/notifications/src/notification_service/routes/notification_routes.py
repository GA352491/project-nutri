from fastapi import APIRouter, Depends, BackgroundTasks
from typing import Dict, Any, List
import uuid
import asyncio

from ..schemas.notification_schemas import CreateNotificationRequest, NotificationResponse
from ..services.notification_service import create_notification, get_user_notifications, mark_as_read, mark_all_as_read
from ..services.email_service import email_service, EmailPayload
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(user: Dict = Depends(get_current_user)):
    return await get_user_notifications(user_uuid(user))

@router.post("/internal/create", response_model=NotificationResponse)
async def internal_create(req: CreateNotificationRequest):
    """Internal endpoint for other microservices to trigger notifications."""
    return await create_notification(req)

@router.patch("/{notif_id}/read", response_model=NotificationResponse)
async def read_notification(notif_id: str, user: Dict = Depends(get_current_user)):
    return await mark_as_read(notif_id, user_uuid(user))

@router.post("/read-all")
async def read_all(user: Dict = Depends(get_current_user)):
    await mark_all_as_read(user_uuid(user))
    return {"status": "success"}

# ── Synchronous Email (direct dispatch) ───────────────────────────────────────

@router.post("/email/send")
async def send_transactional_email(payload: EmailPayload):
    """
    Synchronous email dispatch for low-volume transactional messages.
    Use /email/queue/* for high-volume or background sending.
    """
    return await email_service.send_email(payload)

@router.post("/email/welcome")
async def trigger_welcome_email(email: str, name: str = "Member"):
    """Quick trigger for onboarding welcome email (synchronous)."""
    return await email_service.send_email(EmailPayload(
        to_email=email,
        recipient_name=name,
        template="welcome"
    ))

# ── Async Queue Endpoints (fire-and-forget via Redis queue) ──────────────────

@router.post("/email/queue/welcome")
async def queue_welcome_email(email: str, name: str = "Member", user_id: str = ""):
    """
    Enqueues a welcome email to the Redis async queue.
    Returns immediately — email is dispatched by the background worker.
    """
    try:
        from nutriplan_shared.email_queue import email_queue
        event_id = await email_queue.publish_welcome(to_email=email, name=name, user_id=user_id)
        return {"queued": True, "event_id": event_id, "channel": "nutriplan:email:requested"}
    except Exception as e:
        # Fallback to synchronous delivery
        result = await email_service.send_email(EmailPayload(
            to_email=email, recipient_name=name, template="welcome"
        ))
        return {"queued": False, "fallback": "synchronous", "result": result}

@router.post("/email/queue/appointment-reminder")
async def queue_appointment_reminder(
    email: str, name: str, provider: str,
    date_time: str, room_url: str, user_id: str = ""
):
    """Enqueues an appointment reminder email to the async Redis queue."""
    try:
        from nutriplan_shared.email_queue import email_queue
        event_id = await email_queue.publish_appointment_reminder(
            to_email=email, name=name, provider_name=provider,
            date_time=date_time, room_url=room_url, user_id=user_id
        )
        return {"queued": True, "event_id": event_id}
    except Exception as e:
        result = await email_service.send_email(EmailPayload(
            to_email=email, recipient_name=name, template="appointment_reminder",
            data={"provider_name": provider, "date_time": date_time, "room_url": room_url}
        ))
        return {"queued": False, "fallback": "synchronous", "result": result}

@router.post("/email/queue/meal-reminder")
async def queue_meal_reminder(email: str, name: str, meal_type: str = "Lunch", user_id: str = ""):
    """Enqueues a meal logging reminder email to the async Redis queue."""
    try:
        from nutriplan_shared.email_queue import email_queue
        event_id = await email_queue.publish_meal_reminder(
            to_email=email, name=name, meal_type=meal_type, user_id=user_id
        )
        return {"queued": True, "event_id": event_id}
    except Exception as e:
        result = await email_service.send_email(EmailPayload(
            to_email=email, recipient_name=name, template="meal_reminder",
            data={"meal_type": meal_type}
        ))
        return {"queued": False, "fallback": "synchronous", "result": result}

# ── Queue & Cache Stats Endpoint ───────────────────────────────────────────────

@router.get("/admin/queue-stats")
async def queue_stats():
    """Returns Redis email queue depth and dead-letter queue count (for admin dashboard)."""
    try:
        from nutriplan_shared.email_queue import email_queue
        from nutriplan_shared.cache import cache
        return {
            "email_queue": await email_queue.queue_stats(),
            "cache": await cache.stats(),
        }
    except Exception as e:
        return {"error": str(e), "email_queue": {"pending_messages": 0}, "cache": {"connected": False}}
