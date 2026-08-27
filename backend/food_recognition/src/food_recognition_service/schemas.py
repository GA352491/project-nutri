"""
Food Recognition Service — Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class FoodItem(BaseModel):
    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    portion_g: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    # India-specific
    region: Optional[str] = None           # "North Indian", "South Indian", etc.
    is_indian_cuisine: bool = False
    fssai_code: Optional[str] = None       # FSSAI food category code


class RecognitionResponse(BaseModel):
    image_id: str
    items: List[FoodItem]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    meal_type_guess: str                   # "breakfast" | "lunch" | "dinner" | "snack"
    compliance_warnings: List[str] = []   # FSSAI / USDA rule violations
    logged_to_diary: bool = False
