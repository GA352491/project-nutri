from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class TrackingEvent(Document):
    user_id: Optional[uuid.UUID] = Field(indexed=True)
    session_id: str = Field(indexed=True)
    event_name: str = Field(indexed=True)
    properties: Dict[str, Any] = Field(default_factory=dict)
    platform: str = "web" # web | ios | android
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tracking_events"
