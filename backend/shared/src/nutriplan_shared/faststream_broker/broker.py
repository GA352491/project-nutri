"""
FastStream Event-Driven Layer for NutriPlan.

Replaces synchronous HTTP calls between microservices with async events
over Redis Streams (lightweight, free, runs locally).

EVENTS COVERED:
  - steps_updated      → Meal Plan service reacts by adjusting calories
  - plan_generated     → Notification service reacts by sending push notification
  - appointment_booked → Booking workflow starts via Temporal

HOW TO RUN LOCALLY:
  1. `brew install redis && redis-server`   (start Redis locally)
  2. `python -m faststream_broker.broker run`

FREE & OPEN SOURCE: https://github.com/airtai/faststream
"""
from __future__ import annotations

import os
from typing import Any
from faststream import FastStream
from faststream.redis import RedisBroker
from pydantic import BaseModel

_REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_TEMPORAL_HOST: str = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")

# ── Message Schemas ───────────────────────────────────────────────────────────

class StepsUpdatedEvent(BaseModel):
    user_id: str
    steps: int
    active_calories: float
    date: str  # YYYY-MM-DD


class PlanGeneratedEvent(BaseModel):
    user_id: str
    plan_id: str
    total_calories: int
    mode: str  # "ai" | "curated"


class AppointmentBookedEvent(BaseModel):
    appointment_id: str
    user_id: str
    nutritionist_id: str
    amount_usd: float


# ── Broker Setup ──────────────────────────────────────────────────────────────

broker = RedisBroker(_REDIS_URL)
app = FastStream(broker)


# ── Subscribers (Event Handlers) ──────────────────────────────────────────────

@broker.subscriber("steps_updated")
async def on_steps_updated(event: StepsUpdatedEvent):
    """
    Wearable Service publishes this when new step data arrives.
    Meal Plan Service listens and dynamically adjusts the user's 
    calorie target for the day based on TDEE recalculation.
    """
    print(f"[FastStream] steps_updated for user {event.user_id}: {event.steps} steps, {event.active_calories} kcal burned")
    # In production: call plan_adjuster to update today's calorie budget


@broker.subscriber("plan_generated")
async def on_plan_generated(event: PlanGeneratedEvent):
    """
    Meal Plan Service publishes this when a plan is generated.
    Notification Service reacts by sending a push notification to the mobile app.
    """
    print(f"[FastStream] plan_generated for user {event.user_id}: plan {event.plan_id} ({event.mode} mode, {event.total_calories} kcal)")
    # In production: call Notification Service


@broker.subscriber("appointment_booked")
async def on_appointment_booked(event: AppointmentBookedEvent):
    """
    Appointment Service publishes this when a booking is confirmed.
    This triggers the Temporal BookingWorkflow to handle Stripe + Jitsi.
    """
    from temporalio.client import Client
    print(f"[FastStream] appointment_booked: {event.appointment_id}, triggering Temporal workflow...")
    try:
        client = await Client.connect(_TEMPORAL_HOST)
        await client.start_workflow(
            "BookingWorkflow",
            args=[
                event.appointment_id,
                event.user_id,
                200.0,  # mock: get real amount from DB
                "Dr. Smith",
                f"acct_{event.nutritionist_id}",
            ],
            id=f"booking-{event.appointment_id}",
            task_queue="booking-task-queue",
        )
    except Exception as e:
        print(f"[FastStream] Warning: Could not connect to Temporal: {e}")


# ── Publisher helpers ──────────────────────────────────────────────────────────

async def publish_steps_updated(user_id: str, steps: int, active_calories: float, date: str):
    async with broker:
        await broker.publish(
            StepsUpdatedEvent(user_id=user_id, steps=steps, active_calories=active_calories, date=date),
            channel="steps_updated"
        )

async def publish_plan_generated(user_id: str, plan_id: str, total_calories: int, mode: str):
    async with broker:
        await broker.publish(
            PlanGeneratedEvent(user_id=user_id, plan_id=plan_id, total_calories=total_calories, mode=mode),
            channel="plan_generated"
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())
