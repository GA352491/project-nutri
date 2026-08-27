from typing import Optional
import uuid
from fastapi import HTTPException, status
from ..models.profile import UserProfile
from ..schemas.profile_schemas import ProfileUpdateRequest, ProfileResponse

# ── Profile Service (Direct MongoDB ODM Beanie Operations) ────────
async def get_or_create_profile(user_id: uuid.UUID, full_name: str) -> UserProfile:
    profile = await UserProfile.find_one(UserProfile.user_id == user_id)
    if not profile:
        profile = UserProfile(
            user_id=user_id,
            full_name=full_name,
            age=28,
            gender="other",
            height_cm=175.0,
            weight_kg=70.0,
            activity_level="moderate",
            dietary_preference="vegetarian",
            allergies=[],
            primary_goal="maintain_weight",
            target_weight_kg=68.0
        )
        await profile.insert()
    return profile

async def get_profile(user_id: uuid.UUID) -> ProfileResponse:
    profile = await UserProfile.find_one(UserProfile.user_id == user_id)
    if not profile:
        profile = await get_or_create_profile(user_id, "User")
    
    return ProfileResponse(
        user_id=profile.user_id,
        full_name=profile.full_name,
        age=profile.age,
        gender=profile.gender,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        dietary_preference=profile.dietary_preference,
        regional_preference=profile.regional_preference or "in_south_andhra",
        spice_tolerance=profile.spice_tolerance or "medium",
        home_cooking_oil=profile.home_cooking_oil or "cold_pressed",
        allergies=profile.allergies or [],
        primary_goal=profile.primary_goal,
        target_weight_kg=profile.target_weight_kg
    )

async def update_profile(user_id: uuid.UUID, req: ProfileUpdateRequest, full_name: str) -> ProfileResponse:
    profile = await get_or_create_profile(user_id, full_name)
    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)
    await profile.save()
    return await get_profile(user_id)
