from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

class TrackEventRequest(BaseModel):
    session_id: str
    event_name: str
    properties: Dict[str, Any] = {}
    platform: str = "web"

class TrackEventResponse(BaseModel):
    status: str = "success"
    event_id: str
