import uuid
from typing import List, Optional
from datetime import datetime

from ..models.chat import ChatMessage, Conversation
from ..schemas.chat_schemas import SendMessageRequest, MessageResponse, ConversationResponse

# Canned AI responses for local dev (Phase 2: plug in OpenAI / Gemini)
_AI_RESPONSES = [
    "Based on your profile, I'd suggest adding more legumes to your diet — dal is an excellent source of plant protein that fits within your budget and calorie goals.",
    "Your iron intake seems lower than your ICMR target. Try incorporating spinach (palak), fenugreek leaves (methi), or sesame seeds into your meals this week.",
    "Great job logging your meals consistently! Your average protein intake this week is 87g/day. Let's bump that up to 120g by adding a protein-rich snack like roasted chana.",
    "I noticed you skipped dinner twice this week. Skipping meals can affect your metabolism. Would you like me to suggest some quick 15-minute dinner recipes?",
    "Your grocery budget of ₹3,000/week is well-optimised. The meal plan I generated for you this week comes to approximately ₹2,650.",
]

_ai_idx = 0

async def get_or_create_conversation(user_id: uuid.UUID, conversation_id: Optional[uuid.UUID]) -> Conversation:
    if conversation_id:
        conv = await Conversation.find_one(Conversation.id == conversation_id)
        if conv:
            return conv

    conv = Conversation(user_id=user_id, title="New Conversation")
    await conv.insert()
    return conv


async def send_message(user_id: uuid.UUID, req: SendMessageRequest) -> List[MessageResponse]:
    global _ai_idx
    conv = await get_or_create_conversation(user_id, req.conversation_id)

    # Save user message
    user_msg = ChatMessage(
        conversation_id=conv.id,
        user_id=user_id,
        role="user",
        content=req.content,
    )
    await user_msg.insert()

    # Mock AI reply (Phase 2: call LLM)
    ai_content = _AI_RESPONSES[_ai_idx % len(_AI_RESPONSES)]
    _ai_idx += 1

    ai_msg = ChatMessage(
        conversation_id=conv.id,
        user_id=user_id,
        role="assistant",
        content=ai_content,
    )
    await ai_msg.insert()

    return [
        MessageResponse(
            id=str(user_msg.id), conversation_id=conv.id,
            role="user", content=user_msg.content, timestamp=user_msg.timestamp
        ),
        MessageResponse(
            id=str(ai_msg.id), conversation_id=conv.id,
            role="assistant", content=ai_msg.content, timestamp=ai_msg.timestamp
        ),
    ]


async def get_history(user_id: uuid.UUID, conversation_id: uuid.UUID) -> List[MessageResponse]:
    messages = await ChatMessage.find(
        ChatMessage.conversation_id == conversation_id,
        ChatMessage.user_id == user_id
    ).sort("+timestamp").to_list()

    return [
        MessageResponse(
            id=str(m.id), conversation_id=m.conversation_id,
            role=m.role, content=m.content, timestamp=m.timestamp
        )
        for m in messages
    ]


async def list_conversations(user_id: uuid.UUID) -> List[ConversationResponse]:
    convs = await Conversation.find(Conversation.user_id == user_id).sort("-created_at").to_list()
    return [ConversationResponse(id=str(c.id), title=c.title, created_at=c.created_at) for c in convs]
