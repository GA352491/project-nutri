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

# ── Global In-Memory Persistent Store ────────────────────────────────────────
# Starts empty — all messages come from real patient/expert WebSocket interactions
_ROOM_MESSAGES: Dict[str, List[Dict[str, Any]]] = {}

# Thread status: 'pending' | 'active' | 'declined'
# Defaults to 'pending' for new rooms so experts must accept before chat unlocks.
_THREAD_STATUSES: Dict[str, str] = {}

# Rich metadata per room for expert intake panel
# { room_id: { patient_email, patient_name, expert_email, intake_summary, initiated_at } }
_THREAD_METADATA: Dict[str, Dict[str, Any]] = {}


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
    """Returns thread status; defaults to 'pending' for new/unknown rooms."""
    return _THREAD_STATUSES.get(room_id, "pending")


# ── Thread Metadata Helpers ───────────────────────────────────────────────────

def set_thread_metadata(
    room_id: str,
    patient_email: str,
    expert_email: str,
    patient_name: str = "",
    intake_summary: str = "",
) -> None:
    """Store or update intake metadata for a clinical room."""
    if room_id not in _THREAD_METADATA:
        _THREAD_METADATA[room_id] = {
            "patient_email": patient_email,
            "expert_email": expert_email,
            "patient_name": patient_name or patient_email.split("@")[0].title(),
            "intake_summary": intake_summary,
            "initiated_at": datetime.utcnow().isoformat(),
        }
    else:
        # Allow updating name/summary without overwriting timestamps
        if patient_name:
            _THREAD_METADATA[room_id]["patient_name"] = patient_name
        if intake_summary:
            _THREAD_METADATA[room_id]["intake_summary"] = intake_summary


def get_thread_metadata(room_id: str) -> Dict[str, Any]:
    return _THREAD_METADATA.get(room_id, {})


def get_threads_for_expert(expert_email: str) -> List[Dict[str, Any]]:
    """Return all threads involving this expert email, with metadata and last message."""
    expert_lower = expert_email.strip().lower()
    threads = []
    for room_id, status in _THREAD_STATUSES.items():
        if expert_lower not in room_id:
            continue
        meta = _THREAD_METADATA.get(room_id, {})
        messages = _ROOM_MESSAGES.get(room_id, [])
        last_msg = messages[-1] if messages else {}
        threads.append({
            "room_id": room_id,
            "status": status,
            "patient_email": meta.get("patient_email", ""),
            "patient_name": meta.get("patient_name", ""),
            "expert_email": meta.get("expert_email", expert_email),
            "intake_summary": meta.get("intake_summary", ""),
            "initiated_at": meta.get("initiated_at", ""),
            "last_message": last_msg.get("text", "No messages yet"),
            "last_time": last_msg.get("time", ""),
            "unread_count": sum(1 for m in messages if m.get("sender") == "patient"),
        })
    # Sort: pending first, then by latest activity
    threads.sort(key=lambda t: (0 if t["status"] == "pending" else 1, t.get("initiated_at", "")), reverse=False)
    return threads


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
