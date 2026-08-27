"""
Master Temporal Unified Worker Runner for NutriPlan.

Hosts and runs all microservice durable workflows concurrently:
  1. BookingWorkflow (Telehealth booking saga)
  2. MealPlanWorkflow (AI meal generation + clinical guardrails)
  3. SubscriptionLifecycleWorkflow (Trial, billing, and dunning)
  4. AppointmentReminderWorkflow (T-24h & T-15m alerts)
  5. GroceryDeliverySagaWorkflow (10-minute grocery saga with rollback)
"""
from __future__ import annotations

import asyncio
import os
import sys

# Add microservices and shared modules to Python path
ROOT_DIR = "/Users/anishganga/Project-nutri"
sys.path.extend([
    os.path.join(ROOT_DIR, "backend/shared/src"),
    os.path.join(ROOT_DIR, "backend/appointment/src"),
    os.path.join(ROOT_DIR, "backend/meal_plan/src"),
    os.path.join(ROOT_DIR, "backend/subscriptions/src"),
    os.path.join(ROOT_DIR, "backend/notifications/src"),
    os.path.join(ROOT_DIR, "backend/delivery/src"),
    os.path.join(ROOT_DIR, "backend/payment/src"),
])

from temporalio.client import Client
from temporalio.worker import Worker

# 1. Appointment Booking
from appointment_service.temporal_workers.booking_worker import (
    BookingWorkflow,
    charge_stripe,
    provision_jitsi_room,
    send_confirmation_email,
    update_appointment_db,
)

# 2. Meal Plan Generation
from meal_plan_service.temporal_workers.meal_plan_worker import (
    MealPlanWorkflow,
    fetch_user_context,
    generate_and_validate_meals,
    sync_plan_groceries,
    notify_plan_ready,
)

# 3. Subscription Lifecycle
from subscription_service.temporal_workers.subscription_worker import (
    SubscriptionLifecycleWorkflow,
    send_subscription_email,
    charge_subscription_stripe,
    update_subscription_status,
)

# 4. Appointment Countdown Reminders
from notification_service.temporal_workers.reminder_worker import (
    AppointmentReminderWorkflow,
    send_countdown_notification,
)

# 5. Grocery Delivery Saga
from delivery_service.temporal_workers.grocery_delivery_worker import (
    GroceryDeliverySagaWorkflow,
    reserve_grocery_inventory,
    authorize_stripe_hold,
    dispatch_delivery_rider,
    compensate_cancel_stripe_hold,
)

TEMPORAL_HOST = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")


async def main():
    print(f"[Temporal Hub] Connecting to Temporal Dev Server at {TEMPORAL_HOST}...")
    client = await Client.connect(TEMPORAL_HOST)
    print("[Temporal Hub] Connected successfully. Initializing workers...")

    # Worker 1: Booking Queue
    booking_worker = Worker(
        client,
        task_queue="booking-task-queue",
        workflows=[BookingWorkflow],
        activities=[charge_stripe, provision_jitsi_room, send_confirmation_email, update_appointment_db],
    )

    # Worker 2: Meal Plan Queue
    meal_plan_worker = Worker(
        client,
        task_queue="meal-plan-task-queue",
        workflows=[MealPlanWorkflow],
        activities=[fetch_user_context, generate_and_validate_meals, sync_plan_groceries, notify_plan_ready],
    )

    # Worker 3: Subscription Queue
    sub_worker = Worker(
        client,
        task_queue="subscription-task-queue",
        workflows=[SubscriptionLifecycleWorkflow],
        activities=[send_subscription_email, charge_subscription_stripe, update_subscription_status],
    )

    # Worker 4: Reminder Queue
    reminder_worker = Worker(
        client,
        task_queue="reminder-task-queue",
        workflows=[AppointmentReminderWorkflow],
        activities=[send_countdown_notification],
    )

    # Worker 5: Grocery Delivery Saga Queue
    grocery_worker = Worker(
        client,
        task_queue="grocery-delivery-task-queue",
        workflows=[GroceryDeliverySagaWorkflow],
        activities=[reserve_grocery_inventory, authorize_stripe_hold, dispatch_delivery_rider, compensate_cancel_stripe_hold],
    )

    print("[Temporal Hub] 🚀 All 5 Temporal Workers are live and listening on:")
    print("  - booking-task-queue")
    print("  - meal-plan-task-queue")
    print("  - subscription-task-queue")
    print("  - reminder-task-queue")
    print("  - grocery-delivery-task-queue")
    print("  👉 Temporal Web UI: http://localhost:8233/workflows\n")

    await asyncio.gather(
        booking_worker.run(),
        meal_plan_worker.run(),
        sub_worker.run(),
        reminder_worker.run(),
        grocery_worker.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
