from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from ..services.rag_engine import rag_engine
import json

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_json(self, data: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(data))


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    T-127: Streamed chat API via WebSockets with token-level streaming.

    Protocol:
    - Client sends: plain string message or JSON {"message": "..."}
    - Server emits:
        {"type": "status",     "message": "Thinking..."}    — immediately
        {"type": "token",      "delta": "<chunk>"}           — during streaming
        {"type": "done",       "source": "litellm_stream"}   — on completion
        {"type": "escalation", "message": "..."}             — on clinical trigger
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive user message (plain string or JSON object)
            data = await websocket.receive_text()
            user_msg = data
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict) and "message" in parsed:
                    user_msg = parsed["message"]
            except Exception:
                pass

            # Immediately acknowledge so the UI shows "Thinking..."
            await manager.send_json(
                {"type": "status", "message": "Thinking..."},
                websocket
            )

            # Stream tokens back via generate_response_stream()
            async for chunk in rag_engine.generate_response_stream(
                query=user_msg,
                user_id=user_id
            ):
                await manager.send_json(chunk, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        try:
            await manager.send_json(
                {"type": "error", "message": "Connection error. Please refresh."},
                websocket
            )
        except Exception:
            pass
        manager.disconnect(websocket)
