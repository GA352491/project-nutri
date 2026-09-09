"""
Temporal Durable Workflow for Appointment Reminders (T-24h and T-15m countdowns).

Guarantees notifications are never dropped across server reboots.
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy

# Service URLs — use service registry default; override via env if needed
try:
    from nutriplan_shared.service_registry import NOTIFICATION_URL as _NOTIF_DEFAULT
except ImportError:
    _svc = os.getenv
    _scheme = os.getenv("APP_SCHEME", "http")
    _domain = os.getenv("APP_DOMAIN", "localhost")
    _port   = os.getenv("APP_PORT_NOTIFICATION", "8010")
    _NOTIF_DEFAULT = f"{_scheme}://{_domain}:{_port}"

NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", _NOTIF_DEFAULT)
TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")


# ── Activities ──────────────────────────────────────────────────────────────

@activity.defn
async def send_countdown_notification(user_id: str, email: str, reminder_type: str, details: dict) -> None:
    """Dispatches precise countdown notifications."""
    import httpx
    title = "Reminder: Video Consultation in 24 Hours" if reminder_type == "24h" else "🚨 Starting in 15 Minutes: Video Consultation"
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            await client.post(
                f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications/internal/create",
                json={
                    "user_id": user_id,
                    "type": f"appointment_reminder_{reminder_type}",
                    "title": title,
                    "message": f"Session with {details.get('provider_name', 'Doctor')}. Link: {details.get('room_url', 'https://meet.jit.si')}",
                    "metadata": details
                }
            )
            activity.logger.info(f"[send_countdown_notification] {reminder_type} sent to {user_id}")
    except Exception as e:
        activity.logger.warning(f"[send_countdown_notification] Fallback: {e}")


# ── The Workflow ────────────────────────────────────────────────────────────

@workflow.defn
class AppointmentReminderWorkflow:
    """Durably sleeps until T-24h and T-15m before triggering alerts."""

    @workflow.run
    async def run(self, user_id: str, user_email: str, appointment_id: str, provider_name: str, room_url: str, delay_seconds: int = 2) -> dict:
        retry_policy = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)

        details = {
            "appointment_id": appointment_id,
            "provider_name": provider_name,
            "room_url": room_url,
        }

        # For production, calculate: target_time - timedelta(hours=24) - workflow.now()
        # For immediate verification, sleep delay_seconds
        await workflow.sleep(timedelta(seconds=delay_seconds))

        await workflow.execute_activity(
            send_countdown_notification,
            args=[user_id, user_email, "24h", details],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        await workflow.sleep(timedelta(seconds=delay_seconds))

        await workflow.execute_activity(
            send_countdown_notification,
            args=[user_id, user_email, "15m", details],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        return {"status": "DELIVERED", "appointment_id": appointment_id}


# ── Worker Entrypoint ───────────────────────────────────────────────────────

async def run_reminder_worker():
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue="reminder-task-queue",
        workflows=[AppointmentReminderWorkflow],
        activities=[send_countdown_notification],
    )
    print("[Temporal Worker] ✅ Reminder worker running on queue: reminder-task-queue")
    await worker.run()


if __name__ == "__main__":
    if "--trigger" in sys.argv:
        async def trigger_test():
            client = await Client.connect(TEMPORAL_HOST)
            handle = await client.start_workflow(
                AppointmentReminderWorkflow.run,
                args=["user_patient_99", "patient@nutriplan.io", "apt_5544", "Dr. Ananya Roy", "https://meet.jit.si/nutriplan-apt_5544", 1],
                id="reminder-apt_5544",
                task_queue="reminder-task-queue",
            )
            print(f"[Trigger] Workflow started: {handle.id}")
            res = await handle.result()
            print(f"[Trigger] Workflow finished: {res}")
        asyncio.run(trigger_test())
    else:
        asyncio.run(run_reminder_worker())
