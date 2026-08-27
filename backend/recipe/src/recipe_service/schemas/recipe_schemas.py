from pydantic import BaseModel
from typing import List, Optional
from ..models.food_item import Macronutrients, Micronutrients

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    max_prep_time: Optional[int] = None
    tags: List[str] = []

class RecipeSummary(BaseModel):
    id: str
    title: str
    cuisine: str
    prep_time_minutes: int
    cook_time_minutes: int
    total_macros: Macronutrients
    tags: List[str]

class IngredientInput(BaseModel):
    food_item_name: str  # Free-text name; resolved to a FoodItem on the backend
    quantity: float
    unit: str

class MacrosInput(BaseModel):
    calories_kcal: float = 0.0
    protein_g: float = 0.0
    fat_g: float = 0.0
    carbs_g: float = 0.0
    fiber_g: float = 0.0

class CreateRecipeRequest(BaseModel):
    title: str
    description: str
    cuisine: str
    prep_time_minutes: int
    cook_time_minutes: int
    instructions: List[str]
    tags: List[str] = []
    image_url: Optional[str] = None
    total_macros: MacrosInput = MacrosInput()

class UpdateRecipeRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cuisine: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    instructions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    total_macros: Optional[MacrosInput] = None
