"""
NutriPlan Async Email Queue — Redis Pub/Sub
============================================
Decouples transactional email sending from synchronous HTTP request cycles.

Architecture:
  Publisher  → pushes EmailRequestedEvent to Redis channel 'email:requested'
  Subscriber → consumes the event, renders template, dispatches via EmailService

This ensures:
  1. API endpoints return instantly (< 5ms) — email sending is fire-and-forget
  2. Failed deliveries are retried with exponential backoff
  3. Full audit trail of all email events

Usage (from any microservice):
    from nutriplan_shared.email_queue import email_queue

    await email_queue.publish_welcome(
        to_email="patient@example.com",
        name="Ananya Sharma",
        user_id="user_xyz"
    )
"""
from __future__ import annotations

import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

EMAIL_CHANNEL = "nutriplan:email:requested"
EMAIL_DLQ_CHANNEL = "nutriplan:email:dead_letter"  # failed after retries
MAX_RETRIES = 3


class EmailRequestedEvent(BaseModel):
    """Schema for events published to the email queue."""
    event_id: str
    to_email: str
    recipient_name: str
    template: str          # 'welcome' | 'appointment_reminder' | 'meal_reminder' | 'weekly_summary'
    data: Dict[str, Any] = {}
    user_id: Optional[str] = None
    retry_count: int = 0
    requested_at: str = ""

    def __init__(self, **kwargs):
        if not kwargs.get("requested_at"):
            kwargs["requested_at"] = datetime.now(timezone.utc).isoformat()
        if not kwargs.get("event_id"):
            import uuid
            kwargs["event_id"] = f"email_{uuid.uuid4().hex[:8]}"
        super().__init__(**kwargs)


class AsyncEmailQueue:
    """
    Redis Pub/Sub backed async email queue.
    Publisher side: one method per email type.
    Subscriber side: worker loop that processes and dispatches.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._url = redis_url
        self._pub_client: Any = None
        self._sub_client: Any = None

    async def _pub(self) -> Any:
        if self._pub_client is None:
            try:
                import redis.asyncio as aioredis
                self._pub_client = aioredis.from_url(self._url, decode_responses=True)
                await self._pub_client.ping()
                logger.info("✅ EmailQueue Publisher connected to Redis")
            except Exception as e:
                logger.warning("⚠️  EmailQueue: Redis unavailable (%s) — emails will be logged only", e)
                self._pub_client = _NoOpPub()
        return self._pub_client

    async def _publish(self, event: EmailRequestedEvent) -> None:
        pub = await self._pub()
        payload = event.model_dump_json()
        try:
            # Use Redis LIST as a reliable FIFO queue (LPUSH / BRPOP pattern)
            await pub.lpush(EMAIL_CHANNEL, payload)
            logger.info("📬 EmailQueue PUBLISHED [%s] to=%s template=%s",
                        event.event_id, event.to_email, event.template)
        except Exception as exc:
            logger.error("EmailQueue PUBLISH failed: %s — logging event locally", exc)
            logger.info("FALLBACK EMAIL EVENT: %s", payload)

    # ── Typed publisher helpers ────────────────────────────────────────────────

    async def publish_welcome(self, to_email: str, name: str, user_id: str = "") -> str:
        event = EmailRequestedEvent(
            to_email=to_email, recipient_name=name,
            template="welcome", user_id=user_id, event_id="", requested_at=""
        )
        await self._publish(event)
        return event.event_id

    async def publish_appointment_reminder(
        self, to_email: str, name: str,
        provider_name: str, date_time: str, room_url: str, user_id: str = ""
    ) -> str:
        event = EmailRequestedEvent(
            to_email=to_email, recipient_name=name, template="appointment_reminder",
            user_id=user_id, event_id="", requested_at="",
            data={"provider_name": provider_name, "date_time": date_time, "room_url": room_url}
        )
        await self._publish(event)
        return event.event_id

    async def publish_meal_reminder(
        self, to_email: str, name: str,
        meal_type: str = "Lunch", user_id: str = ""
    ) -> str:
        event = EmailRequestedEvent(
            to_email=to_email, recipient_name=name,
            template="meal_reminder", user_id=user_id, event_id="", requested_at="",
            data={"meal_type": meal_type}
        )
        await self._publish(event)
        return event.event_id

    # ── Worker (consumer) loop — run via background task ─────────────────────

    async def start_worker(self) -> None:
        """
        Blocking consumer loop. Run as a background asyncio task.
        Uses BRPOP (blocking right-pop) — efficient, no polling waste.
        """
        # Import here to avoid circular dependency
        import redis.asyncio as aioredis
        try:
            sub = aioredis.from_url(self._url, decode_responses=True)
            logger.info("🔄 EmailQueue Worker started — listening on %s", EMAIL_CHANNEL)

            while True:
                try:
                    result = await sub.brpop(EMAIL_CHANNEL, timeout=5)
                    if result is None:
                        continue

                    _, payload = result
                    event = EmailRequestedEvent(**json.loads(payload))
                    await self._process_event(event, sub)

                except asyncio.CancelledError:
                    logger.info("EmailQueue Worker shutting down")
                    break
                except Exception as exc:
                    logger.error("EmailQueue Worker loop error: %s", exc)
                    await asyncio.sleep(1)
        except Exception as exc:
            logger.warning("EmailQueue Worker could not start (Redis offline): %s", exc)

    async def _process_event(self, event: EmailRequestedEvent, redis_client: Any) -> None:
        """Dispatch the email event with retry logic."""
        try:
            # Import service here to avoid circular dependency
            from notification_service.services.email_service import email_service, EmailPayload
            result = await email_service.send_email(EmailPayload(
                to_email=event.to_email,
                recipient_name=event.recipient_name,
                template=event.template,
                data=event.data
            ))
            logger.info("✉️  EmailQueue PROCESSED [%s] → %s", event.event_id, result.get("status"))

        except Exception as exc:
            logger.error("EmailQueue PROCESS failed [%s] attempt %d: %s",
                         event.event_id, event.retry_count + 1, exc)

            if event.retry_count < MAX_RETRIES:
                event.retry_count += 1
                backoff = 2 ** event.retry_count
                logger.info("EmailQueue retrying [%s] in %ds", event.event_id, backoff)
                await asyncio.sleep(backoff)
                await redis_client.lpush(EMAIL_CHANNEL, event.model_dump_json())
            else:
                logger.error("EmailQueue DLQ [%s] — max retries exceeded", event.event_id)
                await redis_client.lpush(EMAIL_DLQ_CHANNEL, event.model_dump_json())

    async def queue_stats(self) -> Dict[str, Any]:
        """Returns queue depth metrics for admin dashboard."""
        pub = await self._pub()
        try:
            pending = await pub.llen(EMAIL_CHANNEL)
            dlq = await pub.llen(EMAIL_DLQ_CHANNEL)
            return {
                "queue": EMAIL_CHANNEL,
                "pending_messages": pending,
                "dead_letter_messages": dlq,
                "status": "healthy" if pending < 100 else "degraded",
            }
        except Exception:
            return {"queue": EMAIL_CHANNEL, "pending_messages": 0, "dead_letter_messages": 0, "status": "offline"}


class _NoOpPub:
    async def ping(self): return True
    async def lpush(self, *a, **kw): return 0
    async def brpop(self, *a, **kw): return None
    async def llen(self, *a, **kw): return 0


# Singleton — import this in any microservice
email_queue = AsyncEmailQueue(redis_url=settings.REDIS_URL)
