from beanie import Document
from pydantic import Field
from typing import List, Optional
import uuid

class UserProfile(Document):
    user_id: uuid.UUID = Field(indexed=True, unique=True)
    full_name: str
    
    # Demographics
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    
    # Diet & Regional Food Culture
    dietary_preference: Optional[str] = None # e.g. "vegan", "vegetarian", "non_veg", "jain", "eggetarian"
    regional_preference: Optional[str] = "in_south_andhra" # "in_south_andhra", "in_north_punjab", "in_west_maharashtra", "in_east_bengal", "global"
    spice_tolerance: Optional[str] = "medium" # "mild", "medium", "spicy", "extra_spicy"
    home_cooking_oil: Optional[str] = "cold_pressed" # "groundnut_oil", "mustard_oil", "sesame_oil", "ghee", "olive_oil"
    allergies: List[str] = []
    
    # Goals
    primary_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None
    
    class Settings:
        name = "user_profiles"
