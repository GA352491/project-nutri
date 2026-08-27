"""
Chat Service Routes — Real-Time Clinical Messaging

Endpoints:
  GET  /api/v1/chat/clinical/thread/{room_id}/messages  — Load message history
  POST /api/v1/chat/clinical/send                       — Send a message (REST fallback)
  POST /api/v1/chat/clinical/intake/accept              — Expert accepts patient intake
  GET  /api/v1/chat/clinical/threads/{email}            — List all threads for a user
  WS   /api/v1/chat/ws/clinical/{room_id}/{sender_email} — Real-time WebSocket room
"""
import json
import logging
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Any, List
import uuid

from ..schemas.chat_schemas import (
    SendMessageRequest, MessageResponse, ConversationResponse,
    SendClinicalMessageRequest, AcceptIntakeRequest, ThreadSummaryResponse
)
from ..services.chat_service import (
    send_message, get_history, list_conversations,
    manager, get_canonical_room_id, save_clinical_message,
    get_room_messages, set_thread_status, get_thread_status,
    _THREAD_STATUSES, _ROOM_MESSAGES,
)
from nutriplan_shared.auth import get_current_user, user_uuid

logger = logging.getLogger("chat-service")
router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


# ── Legacy REST endpoints (backward compat) ────────────────────────────────────

@router.get("/conversations", response_model=List[ConversationResponse], summary="List conversations")
async def get_conversations(user: Dict = Depends(get_current_user)):
    return await list_conversations(user_uuid(user))


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: uuid.UUID, user: Dict = Depends(get_current_user)):
    return await get_history(user_uuid(user), conversation_id)


@router.post("/send", response_model=List[MessageResponse], summary="Send AI chat message")
async def send(req: SendMessageRequest, user: Dict = Depends(get_current_user)):
    return await send_message(user_uuid(user), req)


# ── Clinical Real-Time REST endpoints ─────────────────────────────────────────

@router.get(
    "/clinical/thread/{room_id}/messages",
    summary="Load clinical thread message history",
    response_model=List[Dict]
)
async def get_clinical_messages(room_id: str):
    """Returns the full message history for a clinical room, no auth (frontend validates)."""
    messages = get_room_messages(room_id)
    return messages


@router.get(
    "/clinical/threads/{email}",
    summary="List all clinical threads for a user email",
)
async def get_clinical_threads(email: str):
    """Returns all threads where this email is a participant."""
    email_lower = email.strip().lower()
    threads = []
    for room_id, status in _THREAD_STATUSES.items():
        if email_lower in room_id:
            messages = _ROOM_MESSAGES.get(room_id, [])
            last_msg = messages[-1] if messages else {}
            threads.append({
                "room_id": room_id,
                "status": status,
                "last_message": last_msg.get("text", "No messages yet"),
                "last_time": last_msg.get("time", ""),
                "unread_count": 0,
            })
    return threads


@router.post("/clinical/send", summary="Send clinical message (REST fallback)")
async def send_clinical_message(req: SendClinicalMessageRequest):
    """REST endpoint for sending clinical messages — WebSocket is preferred for real-time."""
    room_id = get_canonical_room_id(req.sender_email, req.recipient_email)
    thread_status = get_thread_status(room_id)

    if thread_status == "pending" and req.sender == "patient":
        raise HTTPException(
            status_code=403,
            detail="Clinical thread is pending expert approval. Patient messaging is locked until consent is granted."
        )

    attachment = req.attachment.model_dump() if req.attachment else None
    msg = save_clinical_message(
        room_id=room_id,
        sender=req.sender,
        sender_email=req.sender_email,
        recipient_email=req.recipient_email,
        text=req.text,
        attachment=attachment,
    )

    # Broadcast to all websocket listeners in this room
    await manager.broadcast_to_room(room_id, {"type": "clinical_message", "payload": msg})

    return {"ok": True, "message": msg}


@router.post("/clinical/intake/accept", summary="Expert accepts patient intake request")
async def accept_intake(req: AcceptIntakeRequest):
    """Expert accepts a pending intake request — unlocks two-way messaging."""
    room_id = get_canonical_room_id(req.patient_email, req.expert_email)
    set_thread_status(room_id, "active")

    welcome_text = req.welcome_message or (
        f"Hello! I (Dr. Sarah Jenkins, {req.expert_email}) have accepted your clinical consultation request. "
        "Your two-way messaging care window is now active. How can I assist you with your diet plan today?"
    )

    msg = save_clinical_message(
        room_id=room_id,
        sender="expert",
        sender_email=req.expert_email,
        recipient_email=req.patient_email,
        text=welcome_text,
    )

    # Notify the patient in real-time
    await manager.broadcast_to_room(room_id, {
        "type": "intake_accepted",
        "payload": {
            "room_id": room_id,
            "status": "active",
            "welcome_message": msg,
        }
    })

    return {"ok": True, "room_id": room_id, "status": "active", "message": msg}


@router.post("/clinical/intake/decline", summary="Expert declines patient intake request")
async def decline_intake(patient_email: str, expert_email: str = "expert@nutriplan.local"):
    room_id = get_canonical_room_id(patient_email, expert_email)
    set_thread_status(room_id, "declined")

    await manager.broadcast_to_room(room_id, {
        "type": "intake_declined",
        "payload": {"room_id": room_id, "status": "declined"}
    })

    return {"ok": True, "room_id": room_id, "status": "declined"}


@router.get("/clinical/thread/{room_id}/status", summary="Get consent/thread status")
async def get_clinical_thread_status(room_id: str):
    return {"room_id": room_id, "status": get_thread_status(room_id)}


# ── Real-Time WebSocket Endpoint ───────────────────────────────────────────────

@router.websocket("/ws/clinical/{room_id}/{sender_email}")
async def clinical_chat_ws(websocket: WebSocket, room_id: str, sender_email: str):
    """
    Real-Time Clinical WebSocket.

    Connect: ws://localhost:8012/api/v1/chat/ws/clinical/{room_id}/{sender_email}
    
    Messages in:  { "type": "message", "text": "...", "sender": "patient"|"expert",
                    "recipient_email": "...", "attachment": null }
                  { "type": "typing", "is_typing": true }
                  { "type": "ping" }
    
    Messages out: { "type": "clinical_message", "payload": { ...full msg } }
                  { "type": "typing", "sender_email": "...", "is_typing": true }
                  { "type": "thread_status", "status": "active"|"pending"|"declined" }
                  { "type": "pong" }
                  { "type": "history", "messages": [...] }
    """
    await manager.connect(websocket, sender_email, room_id)
    logger.info(f"[Clinical WS] {sender_email} joined room {room_id}")

    try:
        # 1. Send thread status and full history on connect
        thread_status = get_thread_status(room_id)
        history = get_room_messages(room_id)

        await websocket.send_text(json.dumps({
            "type": "thread_status",
            "status": thread_status
        }))
        await websocket.send_text(json.dumps({
            "type": "history",
            "messages": history
        }))

        # 2. Main message loop
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue

            msg_type = payload.get("type", "message")

            if msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
                continue

            if msg_type == "typing":
                # Broadcast typing indicator to other room members
                await manager.broadcast_to_room(room_id, {
                    "type": "typing",
                    "sender_email": sender_email,
                    "is_typing": payload.get("is_typing", False)
                }, exclude=websocket)
                continue

            if msg_type == "message":
                thread_status = get_thread_status(room_id)

                # Anti-spam: patients cannot message in pending threads
                if thread_status == "pending" and payload.get("sender") == "patient":
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "code": "THREAD_PENDING",
                        "detail": "Clinical thread is pending expert approval."
                    }))
                    continue

                attachment = payload.get("attachment")
                msg = save_clinical_message(
                    room_id=room_id,
                    sender=payload.get("sender", "patient"),
                    sender_email=sender_email,
                    recipient_email=payload.get("recipient_email", ""),
                    text=payload.get("text", ""),
                    attachment=attachment,
                )

                # Broadcast to ALL room participants including sender
                await manager.broadcast_to_room(room_id, {
                    "type": "clinical_message",
                    "payload": msg
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, sender_email, room_id)
        logger.info(f"[Clinical WS] {sender_email} left room {room_id}")
    except Exception as e:
        logger.error(f"[Clinical WS] Error for {sender_email}: {e}")
        manager.disconnect(websocket, sender_email, room_id)
