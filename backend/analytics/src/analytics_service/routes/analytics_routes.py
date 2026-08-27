from fastapi import APIRouter, Depends, Header
from typing import Dict, Any, Optional
import uuid

from ..schemas.analytics_schemas import TrackEventRequest, TrackEventResponse
from ..services.analytics_service import track_event

async def optional_mock_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    # In reality, this would decode the JWT but not fail if missing (for anonymous tracking)
    if authorization:
        return {"sub": "00000000-0000-0000-0000-000000000000"}
    return None

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])

@router.post("/track", response_model=TrackEventResponse)
async def track(req: TrackEventRequest, user: Optional[Dict] = Depends(optional_mock_user)):
    user_id = uuid.UUID(user["sub"]) if user else None
    return await track_event(user_id, req)
