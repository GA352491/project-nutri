from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class Notification(Document):
    user_id: uuid.UUID = Field(indexed=True)
    title: str
    body: str
    type: str = "system" # system, reminder, chat, alert
    is_read: bool = False
    action_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"
