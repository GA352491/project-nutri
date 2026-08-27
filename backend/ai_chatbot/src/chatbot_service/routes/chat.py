from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
from ..services.langgraph_agent import process_chat_message
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    T-127: Streamed chat API via WebSockets.
    Now powered by LangGraph multi-agent pipeline:
      - TriageAgent → routes to correct specialist
      - ClinicalEscalationAgent → transfers to human if needed
      - RecipeAgent → handles cooking queries
      - GeneralNutritionAgent → handles general Q&A with RAG
    """
    await manager.connect(websocket)
    try:
        while True:
            # Receive user message (support plain string or JSON object)
            data = await websocket.receive_text()
            user_msg = data
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict) and "message" in parsed:
                    user_msg = parsed["message"]
            except Exception:
                pass

            # Send processing indicator
            await manager.send_personal_message(
                json.dumps({"type": "status", "message": "Thinking..."}),
                websocket
            )

            # Run through LangGraph multi-agent pipeline
            response_text = await process_chat_message(user_id=user_id, message=user_msg)

            # Determine type (escalation vs normal ai_response)
            response_type = "escalation" if "connecting you to" in response_text else "ai_response"
            await manager.send_personal_message(
                json.dumps({"type": response_type, "message": response_text}),
                websocket
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)

