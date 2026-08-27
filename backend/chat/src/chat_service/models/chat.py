from beanie import Document
from pydantic import Field
from typing import List, Optional
import uuid
from datetime import datetime

class ChatMessage(Document):
    conversation_id: uuid.UUID = Field(indexed=True)
    user_id: uuid.UUID = Field(indexed=True)
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Phase 2: add tool_calls, citations, image_url

    class Settings:
        name = "chat_messages"


class Conversation(Document):
    user_id: uuid.UUID = Field(indexed=True, unique=False)
    title: str = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "conversations"
