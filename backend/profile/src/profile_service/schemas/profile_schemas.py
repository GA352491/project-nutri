from pydantic import BaseModel
from typing import List, Optional
import uuid

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    regional_preference: Optional[str] = None
    spice_tolerance: Optional[str] = None
    home_cooking_oil: Optional[str] = None
    allergies: Optional[List[str]] = None
    primary_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None

class ProfileResponse(BaseModel):
    user_id: uuid.UUID
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    dietary_preference: Optional[str] = None
    regional_preference: Optional[str] = "in_south_andhra"
    spice_tolerance: Optional[str] = "medium"
    home_cooking_oil: Optional[str] = "cold_pressed"
    allergies: List[str] = []
    primary_goal: Optional[str] = None
    target_weight_kg: Optional[float] = None

