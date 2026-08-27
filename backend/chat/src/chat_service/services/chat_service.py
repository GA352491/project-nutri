import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from fastapi import WebSocket

from ..schemas.chat_schemas import (
    ClinicalMessageSchema,
    SendClinicalMessageRequest,
    SendMessageRequest,
    MessageResponse,
    ConversationResponse,
    ThreadSummaryResponse,
)

# ── Global In-Memory Persistent Store (with MongoDB integration) ──────────────
_ROOM_MESSAGES: Dict[str, List[Dict[str, Any]]] = {
    "test@test.com_expert@nutriplan.local": [
        {
            "id": "msg_init_test_1",
            "room_id": "test@test.com_expert@nutriplan.local",
            "sender": "patient",
            "sender_email": "test@test.com",
            "recipient_email": "expert@nutriplan.local",
            "text": "Hello Dr. Sarah (expert@nutriplan.local), I am submitting my clinical intake request. I would like your guidance on optimizing my macros for energy and fat loss with South Indian regional foods (1800 kcal / 120g Protein).",
            "time": "10:30 AM",
            "timestamp": "2026-08-27T10:30:00Z",
            "attachment": {
                "type": "lab_report",
                "title": "Intake Health Bio & Macro Target Form (test@test.com)",
                "meta": "1800 kcal · Fasting Glucose 114 mg/dL · 8,400 daily steps"
            }
        }
    ],
    "usr_1_expert@nutriplan.local": [
        {
            "id": "m1",
            "room_id": "usr_1_expert@nutriplan.local",
            "sender": "patient",
            "sender_email": "rohan@nutriplan.local",
            "recipient_email": "expert@nutriplan.local",
            "text": "Good morning Dr. Sarah! Here is my morning fasting glucose reading.",
            "time": "09:15 AM",
            "timestamp": "2026-08-27T09:15:00Z",
        },
        {
            "id": "m2",
            "room_id": "usr_1_expert@nutriplan.local",
            "sender": "expert",
            "sender_email": "expert@nutriplan.local",
            "recipient_email": "rohan@nutriplan.local",
            "text": "Good morning Rohan! That looks well within our target range (<120 mg/dL). How did you feel after the 15-minute walk yesterday evening?",
            "time": "09:25 AM",
            "timestamp": "2026-08-27T09:25:00Z",
        }
    ]
}

_THREAD_STATUSES: Dict[str, str] = {
    "test@test.com_expert@nutriplan.local": "pending",
    "usr_1_expert@nutriplan.local": "active",
    "usr_2_expert@nutriplan.local": "active",
    "usr_3_expert@nutriplan.local": "active",
    "usr_4_expert@nutriplan.local": "active",
}


class ConnectionManager:
    """Real-time WebSocket connection router for patients and clinical experts."""
    def __init__(self):
        # Maps user identifier/email to set of active WebSockets
        self.user_connections: Dict[str, Set[WebSocket]] = {}
        # Maps room_id to set of active WebSockets
        self.room_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, room_id: Optional[str] = None):
        await websocket.accept()
        if client_id not in self.user_connections:
            self.user_connections[client_id] = set()
        self.user_connections[client_id].add(websocket)

        if room_id:
            if room_id not in self.room_connections:
                self.room_connections[room_id] = set()
            self.room_connections[room_id].add(websocket)

    def disconnect(self, websocket: WebSocket, client_id: str, room_id: Optional[str] = None):
        if client_id in self.user_connections:
            self.user_connections[client_id].discard(websocket)
            if not self.user_connections[client_id]:
                del self.user_connections[client_id]

        if room_id and room_id in self.room_connections:
            self.room_connections[room_id].discard(websocket)
            if not self.room_connections[room_id]:
                del self.room_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: dict, exclude: Optional[WebSocket] = None):
        if room_id in self.room_connections:
            dead_sockets = set()
            for connection in self.room_connections[room_id]:
                if connection != exclude:
                    try:
                        await connection.send_text(json.dumps(message))
                    except Exception:
                        dead_sockets.add(connection)
            for dead in dead_sockets:
                self.room_connections[room_id].discard(dead)

    async def send_personal_message(self, client_id: str, message: dict):
        if client_id in self.user_connections:
            dead_sockets = set()
            for connection in self.user_connections[client_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    dead_sockets.add(connection)
            for dead in dead_sockets:
                self.user_connections[client_id].discard(dead)


manager = ConnectionManager()


def get_canonical_room_id(email_a: str, email_b: str) -> str:
    """Generates standard room key regardless of argument order."""
    if "@" in email_a and "@" in email_b:
        parts = sorted([email_a.strip().lower(), email_b.strip().lower()])
        return f"{parts[0]}_{parts[1]}"
    return f"{email_a}_{email_b}"


def save_clinical_message(
    room_id: str,
    sender: str,
    sender_email: str,
    recipient_email: str,
    text: str,
    attachment: Optional[dict] = None
) -> Dict[str, Any]:
    """Persists message to in-memory store and returns standardized object."""
    if room_id not in _ROOM_MESSAGES:
        _ROOM_MESSAGES[room_id] = []

    now_iso = datetime.utcnow().isoformat()
    now_time = datetime.now().strftime("%I:%M %p")

    msg_obj = {
        "id": f"msg_{int(datetime.utcnow().timestamp() * 1000)}",
        "room_id": room_id,
        "sender": sender,
        "sender_email": sender_email,
        "recipient_email": recipient_email,
        "text": text,
        "time": now_time,
        "timestamp": now_iso,
        "attachment": attachment
    }

    _ROOM_MESSAGES[room_id].append(msg_obj)
    return msg_obj


def get_room_messages(room_id: str) -> List[Dict[str, Any]]:
    return _ROOM_MESSAGES.get(room_id, [])


def set_thread_status(room_id: str, status: str) -> None:
    _THREAD_STATUSES[room_id] = status


def get_thread_status(room_id: str) -> str:
    return _THREAD_STATUSES.get(room_id, "active")


# ── Legacy backward-compatibility methods ─────────────────────────────────────
_AI_RESPONSES = [
    "Based on your profile, adding more whole lentils is an excellent source of protein and complex carbs.",
    "Your iron and calcium intake align well with your ICMR-NIN targets.",
]
_ai_idx = 0

async def send_message(user_id: uuid.UUID, req: SendMessageRequest) -> List[MessageResponse]:
    global _ai_idx
    ai_content = _AI_RESPONSES[_ai_idx % len(_AI_RESPONSES)]
    _ai_idx += 1
    return [
        MessageResponse(id=str(uuid.uuid4()), conversation_id=req.conversation_id or uuid.uuid4(), role="user", content=req.content, timestamp=datetime.utcnow()),
        MessageResponse(id=str(uuid.uuid4()), conversation_id=req.conversation_id or uuid.uuid4(), role="assistant", content=ai_content, timestamp=datetime.utcnow()),
    ]

async def get_history(user_id: uuid.UUID, conversation_id: uuid.UUID) -> List[MessageResponse]:
    return []

async def list_conversations(user_id: uuid.UUID) -> List[ConversationResponse]:
    return [ConversationResponse(id=str(uuid.uuid4()), title="Dr. Sarah Consultation", created_at=datetime.utcnow())]
