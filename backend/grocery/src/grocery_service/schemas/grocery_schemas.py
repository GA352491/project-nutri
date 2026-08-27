from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid


class AddItemRequest(BaseModel):
    name: str
    quantity: str = "1"
    unit: str = ""
    category: str = "General"
    source_recipe_id: Optional[str] = None


class ToggleItemRequest(BaseModel):
    is_checked: bool


class GroceryItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    quantity: str
    unit: str
    category: str
    is_checked: bool
    source_recipe_id: Optional[str] = None

    model_config = {"from_attributes": True}


class GroceryListResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    items: List[GroceryItemResponse] = []

    model_config = {"from_attributes": True}


class GenerateFromPlanRequest(BaseModel):
    """Request to auto-generate grocery list from a regional meal plan."""
    regional_preference: str = "in_south_andhra"
    caloric_target: int = 1800
    dietary_flag: str = "vegetarian"
    replace_existing: bool = False


class RegionalGroceryGroupedResponse(BaseModel):
    """Grocery list grouped by aisle/vendor category."""
    total_items: int
    categories: Dict[str, List[Dict[str, Any]]]
    plan_summary: Dict[str, Any] = {}
