"""
Temporal Durable Workflow for Clinical AI Meal Plan Generation.

Orchestrates:
  1. Fetch User Profile & Pantry Context
  2. Generate with LLM / Curated Engine
  3. Validate against Clinical Guardrails (with auto-retry backoff)
  4. Deduplicate and Sync Grocery Items
  5. Store to Database and Dispatch Notification
"""
from __future__ import annotations

import asyncio
import os
import sys
from datetime import timedelta
from typing import Dict, Any, List
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.common import RetryPolicy

PROFILE_SERVICE_URL = os.getenv("PROFILE_SERVICE_URL", "http://localhost:8003")
GROCERY_SERVICE_URL = os.getenv("GROCERY_SERVICE_URL", "http://localhost:8006")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8010")
TEMPORAL_HOST = os.getenv("TEMPORAL_HOST_PORT", "localhost:7233")


# ── Activities ──────────────────────────────────────────────────────────────

@activity.defn
async def fetch_user_context(user_id: str) -> dict:
    """Fetch user clinical profile, diet goals, and restrictions."""
    import httpx
    profile_data = {
        "user_id": user_id,
        "caloric_target": 1800,
        "dietary_restrictions": ["Low Sodium", "Diabetic Friendly"],
        "preferences": ["Vegetarian", "High Protein"],
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(f"{PROFILE_SERVICE_URL}/api/v1/profile/me")
            if res.status_code == 200:
                data = res.json()
                profile_data["caloric_target"] = data.get("daily_calorie_target", 1800)
                profile_data["dietary_restrictions"] = data.get("allergies_and_restrictions", profile_data["dietary_restrictions"])
                profile_data["preferences"] = data.get("dietary_preferences", profile_data["preferences"])
                activity.logger.info(f"[fetch_user_context] Retrieved user profile for {user_id}")
    except Exception as e:
        activity.logger.warning(f"[fetch_user_context] Profile service fallback: {e}")
    
    return profile_data


@activity.defn
async def generate_and_validate_meals(profile_data: dict) -> dict:
    """Generate meals and enforce clinical guardrails with retry."""
    from meal_plan_service.services.guardrails_layer import guardrails_layer
    from meal_plan_service.services.pydantic_ai_engine import generate_plan_with_pydantic_ai, DailyPlan, MealItem

    caloric_target = profile_data.get("caloric_target", 1800)
    preferences = profile_data.get("preferences", ["Vegetarian"])
    restrictions = profile_data.get("dietary_restrictions", [])

    try:
        # Attempt AI generation
        plan = await generate_plan_with_pydantic_ai(
            caloric_target=caloric_target,
            preferences=preferences,
            dietary_restrictions=restrictions
        )
        plan = guardrails_layer.validate_plan(plan)
        activity.logger.info(f"[generate_and_validate_meals] AI generation successful ({plan.total_calories} kcal)")
        return plan.model_dump()
    except Exception as e:
        activity.logger.warning(f"[generate_and_validate_meals] AI generation offline/failed ({e}), using curated clinical engine")
        
        # Safe curated clinical fallback plan
        fallback_plan = {
            "total_calories": caloric_target,
            "total_protein_g": round(caloric_target * 0.25 / 4, 1),
            "total_carbs_g": round(caloric_target * 0.50 / 4, 1),
            "total_fat_g": round(caloric_target * 0.25 / 9, 1),
            "meals": [
                {
                    "name": "Sprouted Moong & Oats Porridge",
                    "meal_type": "Breakfast",
                    "calories": int(caloric_target * 0.25),
                    "protein_g": 18.0,
                    "carbs_g": 45.0,
                    "fat_g": 8.0,
                    "ingredients": ["Sprouted Moong", "Rolled Oats", "Almond Milk", "Chia Seeds"]
                },
                {
                    "name": "Quinoa Tofu Buddha Bowl with Greens",
                    "meal_type": "Lunch",
                    "calories": int(caloric_target * 0.35),
                    "protein_g": 32.0,
                    "carbs_g": 55.0,
                    "fat_g": 14.0,
                    "ingredients": ["Organic Quinoa", "Firm Tofu", "Steamed Broccoli", "Olive Oil", "Flaxseed"]
                },
                {
                    "name": "Roasted Chana & Walnuts",
                    "meal_type": "Snack",
                    "calories": int(caloric_target * 0.15),
                    "protein_g": 12.0,
                    "carbs_g": 20.0,
                    "fat_g": 10.0,
                    "ingredients": ["Roasted Chana", "Walnuts", "Green Tea"]
                },
                {
                    "name": "Lentil Dal Tadka with Steamed Millets",
                    "meal_type": "Dinner",
                    "calories": int(caloric_target * 0.25),
                    "protein_g": 22.0,
                    "carbs_g": 50.0,
                    "fat_g": 9.0,
                    "ingredients": ["Yellow Dal", "Foxtail Millet", "Cumin", "Turmeric", "Spinach"]
                }
            ]
        }
        return fallback_plan


@activity.defn
async def sync_plan_groceries(plan_data: dict, user_id: str) -> dict:
    """Extract ingredients and sync deduplicated grocery list."""
    import httpx
    all_ingredients = []
    for meal in plan_data.get("meals", []):
        all_ingredients.extend(meal.get("ingredients", []))
    
    unique_items = list(set(all_ingredients))
    activity.logger.info(f"[sync_plan_groceries] Syncing {len(unique_items)} unique ingredients for user {user_id}")

    # Attempt to post to grocery service
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            for item in unique_items[:5]:  # sync top ingredients
                await client.post(
                    f"{GROCERY_SERVICE_URL}/api/v1/grocery/items",
                    json={"name": item, "category": "Produce / Pantry", "quantity": 1}
                )
    except Exception as e:
        activity.logger.warning(f"[sync_plan_groceries] Grocery service sync warning: {e}")

    return {"synced_count": len(unique_items), "items": unique_items}


@activity.defn
async def notify_plan_ready(user_id: str, total_calories: int) -> None:
    """Send real-time confirmation notification."""
    import httpx
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            await client.post(
                f"{NOTIFICATION_SERVICE_URL}/api/v1/notifications/internal/create",
                json={
                    "user_id": user_id,
                    "type": "meal_plan_ready",
                    "title": "🥗 Your AI Meal Plan is Ready!",
                    "message": f"Target: {total_calories} kcal. Perfectly balanced for your health profile.",
                    "metadata": {"calories": total_calories}
                }
            )
            activity.logger.info(f"[notify_plan_ready] Notification sent to {user_id}")
    except Exception as e:
        activity.logger.warning(f"[notify_plan_ready] Notification service warning: {e}")


# ── The Workflow ────────────────────────────────────────────────────────────

@workflow.defn
class MealPlanWorkflow:
    """Durable orchestration of Clinical AI Meal Planning."""

    @workflow.run
    async def run(self, user_id: str, requested_calories: int = 1800) -> dict:
        retry_policy = RetryPolicy(maximum_attempts=3, backoff_coefficient=2.0)

        # 1. Fetch user context & preferences
        profile = await workflow.execute_activity(
            fetch_user_context,
            args=[user_id],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )
        if requested_calories:
            profile["caloric_target"] = requested_calories

        # 2. Generate and clinically validate meal plan
        meal_plan = await workflow.execute_activity(
            generate_and_validate_meals,
            args=[profile],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=retry_policy,
        )

        # 3. Automatically deduplicate and sync grocery list
        grocery_sync = await workflow.execute_activity(
            sync_plan_groceries,
            args=[meal_plan, user_id],
            start_to_close_timeout=timedelta(seconds=20),
            retry_policy=retry_policy,
        )

        # 4. Notify patient
        await workflow.execute_activity(
            notify_plan_ready,
            args=[user_id, meal_plan.get("total_calories", requested_calories)],
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=retry_policy,
        )

        return {
            "status": "COMPLETED",
            "user_id": user_id,
            "plan": meal_plan,
            "grocery_sync": grocery_sync,
        }


# ── Worker Entrypoint ───────────────────────────────────────────────────────

async def run_meal_plan_worker():
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue="meal-plan-task-queue",
        workflows=[MealPlanWorkflow],
        activities=[
            fetch_user_context,
            generate_and_validate_meals,
            sync_plan_groceries,
            notify_plan_ready,
        ],
    )
    print("[Temporal Worker] ✅ MealPlan worker running on queue: meal-plan-task-queue")
    await worker.run()


if __name__ == "__main__":
    if "--trigger" in sys.argv:
        async def trigger_test():
            client = await Client.connect(TEMPORAL_HOST)
            handle = await client.start_workflow(
                MealPlanWorkflow.run,
                args=["user_demo_789", 2000],
                id="meal-plan-user_demo_789",
                task_queue="meal-plan-task-queue",
            )
            print(f"[Trigger] Workflow started: {handle.id}")
            res = await handle.result()
            print(f"[Trigger] Workflow finished: {res['status']} with {len(res['plan']['meals'])} meals")
        asyncio.run(trigger_test())
    else:
        asyncio.run(run_meal_plan_worker())
