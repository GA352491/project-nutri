from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class CreateNotificationRequest(BaseModel):
    user_id: uuid.UUID
    title: str
    body: str
    type: str = "system"
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = {}

class NotificationResponse(BaseModel):
    id: str
    user_id: uuid.UUID
    title: str
    body: str
    type: str
    is_read: bool
    action_url: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
