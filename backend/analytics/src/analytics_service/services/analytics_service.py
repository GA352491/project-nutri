import uuid
from typing import Optional

from ..models.event import TrackingEvent
from ..schemas.analytics_schemas import TrackEventRequest, TrackEventResponse

async def track_event(user_id: Optional[uuid.UUID], req: TrackEventRequest) -> TrackEventResponse:
    event = TrackingEvent(
        user_id=user_id,
        session_id=req.session_id,
        event_name=req.event_name,
        properties=req.properties,
        platform=req.platform
    )
    await event.insert()
    
    # In Phase 2, this could forward to PostHog, Mixpanel, or Amplitude
    
    return TrackEventResponse(event_id=str(event.id))
