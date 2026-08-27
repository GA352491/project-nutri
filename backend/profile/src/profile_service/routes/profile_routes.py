from fastapi import APIRouter, Depends
from typing import Dict, Any
from ..schemas.profile_schemas import ProfileUpdateRequest, ProfileResponse
from ..services.profile_service import get_profile, update_profile
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])

@router.get(
    "/me",
    response_model=ProfileResponse,
    summary="Get current user profile"
)
async def read_profile(user: Dict[str, Any] = Depends(get_current_user)):
    return await get_profile(user_uuid(user))

@router.put(
    "/me",
    response_model=ProfileResponse,
    summary="Update current user profile"
)
async def write_profile(req: ProfileUpdateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    name = user.get("email", "").split("@")[0]
    return await update_profile(user_uuid(user), req, name)
