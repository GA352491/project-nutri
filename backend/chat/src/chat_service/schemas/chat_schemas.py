from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


class AttachmentSchema(BaseModel):
    type: str  # 'plan' | 'lab_report' | 'meal_photo'
    title: str
    meta: Optional[str] = None


class ClinicalMessageSchema(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{int(datetime.utcnow().timestamp()*1000)}")
    room_id: str
    sender: str  # 'patient' | 'expert'
    sender_email: str
    recipient_email: str
    text: str
    time: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    attachment: Optional[AttachmentSchema] = None


class SendClinicalMessageRequest(BaseModel):
    sender: str = "patient"  # 'patient' | 'expert'
    sender_email: str
    recipient_email: str
    text: str
    attachment: Optional[AttachmentSchema] = None


class AcceptIntakeRequest(BaseModel):
    patient_email: str
    expert_email: str = "expert@nutriplan.local"
    welcome_message: Optional[str] = None


class ThreadSummaryResponse(BaseModel):
    room_id: str
    patient_name: str
    patient_email: str
    expert_name: str
    expert_email: str
    status: str  # 'active' | 'pending' | 'closed'
    last_message: str
    last_time: str
    unread_count: int = 0
    intake_summary: Optional[str] = None


# Legacy schemas for backward compatibility
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
