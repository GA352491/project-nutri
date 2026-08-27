from fastapi import APIRouter, Depends
from typing import Dict, Any
import uuid
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.meal_plan_schemas import GeneratePlanRequest, MealPlanResponse
from ..services.meal_plan_service import generate_weekly_plan, get_current_plan, get_db
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/plan", tags=["Meal Plans"])

@router.post(
    "/generate",
    response_model=MealPlanResponse,
    summary="Generate a new meal plan"
)
async def generate_plan(
    req: GeneratePlanRequest,
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = user_uuid(user)
    return await generate_weekly_plan(user_id, req, db)

@router.get(
    "/current",
    response_model=MealPlanResponse,
    summary="Get current meal plan"
)
async def get_plan(
    user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_id = user_uuid(user)
    return await get_current_plan(user_id, date.today(), db)
