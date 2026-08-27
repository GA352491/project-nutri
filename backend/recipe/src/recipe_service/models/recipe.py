from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import List, Optional
from .food_item import FoodItem, Macronutrients, Micronutrients

class RecipeIngredient(BaseModel):
    name: str = ""
    quantity: float
    unit: str  # e.g. "g", "ml", "cup", "tbsp"

class Recipe(Document):
    title: str = Field(index=True)
    description: str
    cuisine: str = Field(index=True, default="Indian")
    region_id: Optional[str] = Field(index=True, default="in_general")  # 'in_south_andhra', 'in_north_punjab', etc.
    meal_type: str = Field(index=True, default="lunch")                # 'breakfast', 'lunch', 'snack', 'dinner'
    dietary_flag: str = Field(default="vegetarian")                    # 'veg', 'vegan', 'non_veg', 'jain'
    prep_time_minutes: int = 15
    cook_time_minutes: int = 20

    ingredients: List[RecipeIngredient] = []
    instructions: List[str] = []

    # Optional image
    image_url: Optional[str] = None

    # Pre-calculated totals for the entire recipe
    total_macros: Macronutrients
    total_micros: Micronutrients

    tags: List[str] = []  # "vegan", "breakfast", "high-protein", "in_south_andhra"

    class Settings:
        name = "recipes"
