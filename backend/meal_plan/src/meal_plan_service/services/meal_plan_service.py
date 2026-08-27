from typing import List
import uuid
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
import httpx

from ..models.meal_plan import MealPlan, MealPlanItem
from ..schemas.meal_plan_schemas import GeneratePlanRequest, MealPlanResponse
from ..config import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(MealPlan.metadata.create_all)


async def _load_plan(db: AsyncSession, plan_id: uuid.UUID) -> MealPlan:
    result = await db.execute(
        select(MealPlan).options(selectinload(MealPlan.meals)).where(MealPlan.id == plan_id)
    )
    return result.scalars().first()


async def _fetch_recipes() -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(f"{settings.RECIPE_SERVICE_URL}/api/v1/recipes/")
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and data:
                    return data
    except Exception as e:
        print(f"[MealPlan] Recipe service unavailable: {e}")
    return []


async def _fetch_profile(user_id: uuid.UUID) -> dict:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{settings.PROFILE_SERVICE_URL}/api/v1/profile/me")
            if res.status_code == 200:
                return res.json()
    except Exception:
        pass
    return {}


def _meal_from_recipe(recipe: dict, meal_type: str) -> dict:
    macros = recipe.get("total_macros") or {}
    return {
        "recipe_id": str(recipe.get("id") or recipe.get("title")),
        "calories": float(macros.get("calories_kcal") or macros.get("calories") or 450),
        "protein_g": float(macros.get("protein_g") or 25),
        "fat_g": float(macros.get("fat_g") or 15),
        "carbs_g": float(macros.get("carbs_g") or 50),
        "meal_type": meal_type,
    }


async def generate_weekly_plan(user_id: uuid.UUID, req: GeneratePlanRequest, db: AsyncSession) -> MealPlanResponse:
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals))
        .where(
            (MealPlan.user_id == user_id)
            & (MealPlan.start_date <= req.start_date)
            & (MealPlan.end_date >= req.start_date)
        )
    )
    existing = result.scalars().first()
    if existing:
        return MealPlanResponse.model_validate(existing)

    # Use the scientific Regional Constraint Optimizer
    from .regional_optimizer import optimizer
    profile = await _fetch_profile(user_id)
    regional_pref = profile.get("regional_preference") or "in_south_andhra"
    dietary_flag = profile.get("dietary_preference") or "vegetarian"
    allergies = profile.get("allergies") or []

    daily_plan = optimizer.solve_daily_plan(
        caloric_target=2000,
        region_id=regional_pref,
        dietary_flag=dietary_flag,
        allergies=allergies,
    )

    end_date = req.start_date + timedelta(days=req.days - 1)
    targets = {
        "calories": daily_plan["total_calories"],
        "protein": daily_plan["total_protein_g"],
        "fat": daily_plan["total_fat_g"],
        "carbs": daily_plan["total_carbs_g"],
    }

    plan = MealPlan(
        user_id=user_id,
        start_date=req.start_date,
        end_date=end_date,
        targets=targets,
    )
    db.add(plan)

    for i in range(req.days):
        current_date = req.start_date + timedelta(days=i)
        for meal in daily_plan["meals"]:
            db.add(MealPlanItem(
                plan=plan,
                date=current_date,
                meal_type=meal["meal_type"],
                recipe_id=meal["name"],
                calories=float(meal["calories"]),
                protein_g=float(meal["protein_g"]),
                fat_g=float(meal["fat_g"]),
                carbs_g=float(meal["carbs_g"]),
            ))

    await db.commit()
    plan = await _load_plan(db, plan.id)
    return MealPlanResponse.model_validate(plan)


async def get_current_plan(user_id: uuid.UUID, today: date, db: AsyncSession) -> MealPlanResponse:
    result = await db.execute(
        select(MealPlan)
        .options(selectinload(MealPlan.meals))
        .where(
            (MealPlan.user_id == user_id)
            & (MealPlan.start_date <= today)
            & (MealPlan.end_date >= today)
        )
    )
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="No active meal plan found")
    return MealPlanResponse.model_validate(plan)
