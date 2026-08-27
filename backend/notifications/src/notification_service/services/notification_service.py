import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import HTTPException
import logging

from ..schemas.notification_schemas import CreateNotificationRequest, NotificationResponse

logger = logging.getLogger(__name__)

# Resilient in-memory fallback store if MongoDB is offline in local dev
MOCK_NOTIFICATIONS: Dict[str, Dict[str, Any]] = {
  "notif_1": {
    "id": "notif_1",
    "user_id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
    "title": "Welcome to NutriPlan!",
    "body": "Your personalized ICMR-NIN nutrition plan is ready for review.",
    "type": "system",
    "is_read": False,
    "action_url": "/plan",
    "metadata": {},
    "created_at": datetime.now(timezone.utc)
  },
  "notif_2": {
    "id": "notif_2",
    "user_id": uuid.UUID("00000000-0000-0000-0000-000000000000"),
    "title": "Wearable Synced",
    "body": "8,420 steps recorded today. Great job hitting your active goal!",
    "type": "wearable",
    "is_read": False,
    "action_url": "/wearables",
    "metadata": {},
    "created_at": datetime.now(timezone.utc)
  }
}

async def create_notification(req: CreateNotificationRequest) -> NotificationResponse:
    try:
        from ..models.notification import Notification
        notif = Notification(
            user_id=req.user_id,
            title=req.title,
            body=req.body,
            type=req.type,
            action_url=req.action_url,
            metadata=req.metadata
        )
        await notif.insert()
        return NotificationResponse(
            id=str(notif.id),
            user_id=notif.user_id,
            title=notif.title,
            body=notif.body,
            type=notif.type,
            is_read=notif.is_read,
            action_url=notif.action_url,
            metadata=notif.metadata,
            created_at=notif.created_at
        )
    except Exception as e:
        logger.warning(f"MongoDB fallback during create_notification: {e}")
        new_id = f"notif_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        item = {
            "id": new_id,
            "user_id": req.user_id,
            "title": req.title,
            "body": req.body,
            "type": req.type,
            "is_read": False,
            "action_url": req.action_url,
            "metadata": req.metadata,
            "created_at": now
        }
        MOCK_NOTIFICATIONS[new_id] = item
        return NotificationResponse(**item)


async def get_user_notifications(user_id: uuid.UUID) -> List[NotificationResponse]:
    try:
        from ..models.notification import Notification
        notifs = await Notification.find(Notification.user_id == user_id).sort("-created_at").to_list()
        return [
            NotificationResponse(
                id=str(n.id),
                user_id=n.user_id,
                title=n.title,
                body=n.body,
                type=n.type,
                is_read=n.is_read,
                action_url=n.action_url,
                metadata=n.metadata,
                created_at=n.created_at
            )
            for n in notifs
        ]
    except Exception as e:
        logger.warning(f"MongoDB fallback during get_user_notifications: {e}")
        return [
            NotificationResponse(**n) for n in MOCK_NOTIFICATIONS.values()
            if n["user_id"] == user_id or str(user_id).startswith("00000000")
        ]


async def mark_as_read(notif_id: str, user_id: uuid.UUID) -> NotificationResponse:
    try:
        from beanie import PydanticObjectId
        from ..models.notification import Notification
        notif = await Notification.get(PydanticObjectId(notif_id))
        if not notif or notif.user_id != user_id:
            raise HTTPException(status_code=404, detail="Notification not found")
        notif.is_read = True
        await notif.save()
        return NotificationResponse(
            id=str(notif.id),
            user_id=notif.user_id,
            title=notif.title,
            body=notif.body,
            type=notif.type,
            is_read=notif.is_read,
            action_url=notif.action_url,
            metadata=notif.metadata,
            created_at=notif.created_at
        )
    except Exception as e:
        logger.warning(f"MongoDB fallback during mark_as_read: {e}")
        if notif_id in MOCK_NOTIFICATIONS:
            MOCK_NOTIFICATIONS[notif_id]["is_read"] = True
            return NotificationResponse(**MOCK_NOTIFICATIONS[notif_id])
        raise HTTPException(status_code=404, detail="Notification not found")


async def mark_all_as_read(user_id: uuid.UUID) -> None:
    try:
        from ..models.notification import Notification
        notifs = await Notification.find(Notification.user_id == user_id, Notification.is_read == False).to_list()
        for n in notifs:
            n.is_read = True
            await n.save()
    except Exception as e:
        logger.warning(f"MongoDB fallback during mark_all_as_read: {e}")
        for n in MOCK_NOTIFICATIONS.values():
            if n["user_id"] == user_id or str(user_id).startswith("00000000"):
                n["is_read"] = True
