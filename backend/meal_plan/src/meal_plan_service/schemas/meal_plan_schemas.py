from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import date

class MealPlanItemBase(BaseModel):
    date: date
    meal_type: str
    recipe_id: Optional[str] = None
    calories: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    status: str = "planned"

class MealPlanItemResponse(MealPlanItemBase):
    id: uuid.UUID
    plan_id: uuid.UUID

    model_config = {"from_attributes": True}

class MealPlanBase(BaseModel):
    start_date: date
    end_date: date
    status: str = "active"
    targets: Optional[Dict] = None

class MealPlanResponse(MealPlanBase):
    id: uuid.UUID
    user_id: uuid.UUID
    meals: List[MealPlanItemResponse] = []

    model_config = {"from_attributes": True}

class GeneratePlanRequest(BaseModel):
    start_date: date
    days: int = 7
    # Real world app would take dietary preferences from profile service directly
