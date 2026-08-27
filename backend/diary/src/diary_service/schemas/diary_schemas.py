from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import date


# ── Requests ───────────────────────────────────────────────────────

class LogEntryRequest(BaseModel):
    log_date: date = Field(default_factory=date.today)
    meal_type: str = "snack"              # breakfast | lunch | snack | dinner
    food_name: str
    quantity_g: float = 100.0
    calories: float
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: float = 0.0
    recipe_id: Optional[str] = None
    source: str = "manual"
    notes: Optional[str] = None


# ── Responses ──────────────────────────────────────────────────────

class DiaryEntryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    log_date: date
    meal_type: str
    food_name: str
    quantity_g: float
    calories: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    source: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class DailySummaryResponse(BaseModel):
    log_date: date
    total_calories: float
    total_protein_g: float
    total_fat_g: float
    total_carbs_g: float
    total_fiber_g: float
    entry_count: int
    entries: List[DiaryEntryResponse] = []

    model_config = {"from_attributes": True}
