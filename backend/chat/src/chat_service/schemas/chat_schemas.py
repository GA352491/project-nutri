from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime


class SendMessageRequest(BaseModel):
    conversation_id: Optional[uuid.UUID] = None
    content: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: uuid.UUID
    role: str
    content: str
    timestamp: datetime


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
