from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List

class Macronutrients(BaseModel):
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float = 0.0

class Micronutrients(BaseModel):
    calcium_mg: float = 0.0
    iron_mg: float = 0.0
    vitamin_c_mg: float = 0.0
    vitamin_d_mcg: float = 0.0

class FoodItem(Document):
    name: str = Field(index=True)
    source: str = "IFCT"  # IFCT, USDA, USER
    source_id: Optional[str] = None
    category: str

    # Nutritional values typically stored per 100g
    serving_size_g: float = 100.0
    macros: Macronutrients
    micros: Micronutrients

    tags: List[str] = []  # e.g. "vegan", "gluten-free"

    class Settings:
        name = "food_items"
