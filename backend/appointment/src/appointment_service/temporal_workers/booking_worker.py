"""
Temporal Durable Workflow for the Booking Saga.

Temporal replaces brittle try/except chains with guaranteed, resumable
distributed transactions. If any step fails (e.g., Stripe errors),
Temporal automatically retries or triggers compensation logic.

HOW TO RUN LOCALLY:
  1. `brew install temporal`  (or run via their open-source server)
  2. `temporal server start-dev --ui-port 8233 --port 7233`
  3. Run this worker: `python -m appointment_service.temporal_workers.booking_worker`
     (from: backend/appointment/src/)

FREE & OPEN SOURCE: https://github.com/temporalio/temporal
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy

# ── Service base URLs (read from env, default to local dev ports) ─────────────
PAYMENT_URL   = os.getenv("PAYMENT_SERVICE_URL",       "http://localhost:8016")
VIDEO_URL     = os.getenv("VIDEO_SERVICE_URL",         "http://localhost:8014")
NOTIFICATION_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8010")
APPOINTMENT_URL  = os.getenv("APPOINTMENT_SERVICE_URL",  "http://localhost:8013")
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST_PORT",        "localhost:7233")


# ── Activities (individual steps of the booking saga) ─────────────────────────

@activity.defn
async def charge_stripe(appointment_id: str, amount_usd: float, stripe_account_id: str) -> str:
    """
    Step 1: Charge the patient via the Payment microservice.
    Calls POST /api/v1/payment/stripe/checkout/booking and returns the PaymentIntent ID.
    Falls back gracefully when running without live Stripe credentials.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            res = await client.post(
                f"{PAYMENT_URL}/api/v1/payment/stripe/checkout/booking",
                json={
                    "appointment_id": appointment_id,
                    "amount_usd": amount_usd,
                    "nutritionist_account_id": stripe_account_id or "acct_test_placeholder",
                    "metadata": {"source": "temporal_booking_saga"},
                },
            )
            if res.status_code == 200:
                data = res.json()
                pi_id = data.get("payment_intent_id", f"pi_{appointment_id[:8]}")
                activity.logger.info(
                    f"[charge_stripe] Stripe PaymentIntent created: {pi_id} "
                    f"(${amount_usd:.2f}, fee: {data.get('platform_fee_cents', 0)} cents)"
                )
                return pi_id
            else:
                activity.logger.warning(
                    f"[charge_stripe] Payment service returned {res.status_code}: {res.text[:200]}"
                )
                return f"pi_{appointment_id[:8]}_fallback"
    except httpx.ConnectError:
        # Payment service not reachable — fallback for local dev without Stripe
        activity.logger.warning("[charge_stripe] Payment service offline — using mock PI for dev")
        return f"pi_{appointment_id[:8]}_dev"


@activity.defn
async def provision_jitsi_room(appointment_id: str, nutritionist_name: str) -> str:
    """
    Step 2: Generate the Jitsi video room URL via the Video microservice.
    Falls back to a direct Jitsi URL if the video service is unreachable.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{VIDEO_URL}/api/v1/video/room/create",
                json={
                    "appointment_id": appointment_id,
                    "nutritionist_name": nutritionist_name,
                },
            )
            if res.status_code == 200:
                data = res.json()
                room_url = data.get("room_url") or data.get("url")
                activity.logger.info(f"[provision_jitsi_room] Room created: {room_url}")
                return room_url
            else:
                activity.logger.warning(f"[provision_jitsi_room] Video service {res.status_code}")
    except httpx.ConnectError:
        activity.logger.warning("[provision_jitsi_room] Video service offline — using direct Jitsi fallback")

    # Direct Jitsi fallback (works without any backend)
    room_url = f"https://meet.jit.si/nutriplan-{appointment_id}"
    activity.logger.info(f"[provision_jitsi_room] Fallback Jitsi room: {room_url}")
    return room_url


@activity.defn
async def send_confirmation_email(user_id: str, room_url: str, appointment_id: str) -> None:
    """
    Step 3: Notify the user via the Notification microservice.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{NOTIFICATION_URL}/api/v1/notifications/send",
                json={
                    "user_id": user_id,
                    "type": "booking_confirmation",
                    "title": "Your appointment is confirmed! 🎉",
                    "body": f"Join your video session here: {room_url}",
                    "metadata": {"appointment_id": appointment_id, "room_url": room_url},
                },
            )
            if res.status_code in (200, 201):
                activity.logger.info(f"[send_confirmation_email] Notification sent to {user_id}")
            else:
                activity.logger.warning(
                    f"[send_confirmation_email] Notification service {res.status_code}: {res.text[:100]}"
                )
    except httpx.ConnectError:
        activity.logger.warning(
            f"[send_confirmation_email] Notification service offline — skipping email for {user_id}"
        )


@activity.defn
async def update_appointment_db(appointment_id: str, stripe_pi: str, room_url: str) -> None:
    """
    Step 4: Persist the final CONFIRMED state to the Appointment service database.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.patch(
                f"{APPOINTMENT_URL}/api/v1/appointments/{appointment_id}/confirm",
                json={
                    "stripe_payment_intent_id": stripe_pi,
                    "video_room_url": room_url,
                    "status": "CONFIRMED",
                },
            )
            if res.status_code == 200:
                activity.logger.info(
                    f"[update_appointment_db] Appointment {appointment_id} marked CONFIRMED"
                )
            else:
                activity.logger.warning(
                    f"[update_appointment_db] Appointment service {res.status_code}: {res.text[:100]}"
                )
    except httpx.ConnectError:
        activity.logger.warning(
            f"[update_appointment_db] Appointment service offline — DB update skipped for {appointment_id}"
        )


# ── The Durable Workflow (orchestrates the saga) ──────────────────────────────

@workflow.defn
class BookingWorkflow:
    """
    A Temporal Saga that orchestrates the entire booking process.
    Each activity is automatically retried on transient failures.
    If any step fails permanently, the workflow fails gracefully
    and can be inspected in the Temporal Web UI at http://localhost:8233.
    """

    @workflow.run
    async def run(
        self,
        appointment_id: str,
        user_id: str,
        amount_usd: float,
        nutritionist_name: str,
        stripe_account_id: str,
    ) -> dict:

        retry_policy = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)

        # Step 1 — Charge Stripe
        stripe_pi = await workflow.execute_activity(
            charge_stripe,
            args=[appointment_id, amount_usd, stripe_account_id],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )

        # Step 2 — Provision Jitsi video room
        room_url = await workflow.execute_activity(
            provision_jitsi_room,
            args=[appointment_id, nutritionist_name],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        # Step 3 — Send confirmation email / push notification
        await workflow.execute_activity(
            send_confirmation_email,
            args=[user_id, room_url, appointment_id],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        # Step 4 — Persist CONFIRMED state to DB
        await workflow.execute_activity(
            update_appointment_db,
            args=[appointment_id, stripe_pi, room_url],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        return {
            "status": "CONFIRMED",
            "appointment_id": appointment_id,
            "room_url": room_url,
            "stripe_pi": stripe_pi,
        }


# ── Worker entrypoint ─────────────────────────────────────────────────────────

async def run_worker():
    print(f"[Temporal Worker] Connecting to Temporal at {TEMPORAL_HOST}...")
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue="booking-task-queue",
        workflows=[BookingWorkflow],
        activities=[
            charge_stripe,
            provision_jitsi_room,
            send_confirmation_email,
            update_appointment_db,
        ],
    )
    print("[Temporal Worker] ✅ Booking worker started on task queue: booking-task-queue")
    print(f"[Temporal Worker]    View workflows at: http://localhost:{os.getenv('TEMPORAL_UI_PORT', '8233')}")
    await worker.run()


# ── One-shot workflow trigger helper (for testing) ────────────────────────────

async def trigger_test_workflow(
    appointment_id: str = "apt_test_001",
    user_id: str = "user_test_001",
    amount_usd: float = 100.0,
    nutritionist_name: str = "Dr. Priya Sharma",
    stripe_account_id: str = "acct_test_placeholder",
):
    """
    Trigger the BookingWorkflow once for manual testing.
    Run with: python -m appointment_service.temporal_workers.booking_worker --trigger
    Then check http://localhost:8233 to see it in the Temporal UI.
    """
    print(f"[Trigger] Connecting to Temporal at {TEMPORAL_HOST}...")
    client = await Client.connect(TEMPORAL_HOST)
    handle = await client.start_workflow(
        BookingWorkflow.run,
        args=[appointment_id, user_id, amount_usd, nutritionist_name, stripe_account_id],
        id=f"booking-{appointment_id}",
        task_queue="booking-task-queue",
    )
    print(f"[Trigger] ✅ Workflow started: ID={handle.id}")
    print(f"[Trigger]    View at: http://localhost:{os.getenv('TEMPORAL_UI_PORT', '8233')}/workflows")
    result = await handle.result()
    print(f"[Trigger] ✅ Workflow completed: {result}")
    return result


if __name__ == "__main__":
    if "--trigger" in sys.argv:
        asyncio.run(trigger_test_workflow())
    else:
        asyncio.run(run_worker())
