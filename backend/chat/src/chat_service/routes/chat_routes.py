from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import uuid

from ..schemas.chat_schemas import SendMessageRequest, MessageResponse, ConversationResponse
from ..services.chat_service import send_message, get_history, list_conversations
from nutriplan_shared.auth import get_current_user, user_uuid

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.get("/conversations", response_model=List[ConversationResponse], summary="List conversations")
async def get_conversations(user: Dict = Depends(get_current_user)):
    return await list_conversations(user_uuid(user))


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse], summary="Get conversation history")
async def get_messages(conversation_id: uuid.UUID, user: Dict = Depends(get_current_user)):
    return await get_history(user_uuid(user), conversation_id)


@router.post("/send", response_model=List[MessageResponse], summary="Send a message", description="Sends a user message and returns both the user message and the AI reply.")
async def send(req: SendMessageRequest, user: Dict = Depends(get_current_user)):
    return await send_message(user_uuid(user), req)
