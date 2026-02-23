"""Chat API routes — powers the Vellichor AI chatbot."""

from fastapi import APIRouter, Depends
from datetime import datetime
from bson import ObjectId

from auth import get_current_user
from models import ChatMessage, ChatResponse
from database import conversations_collection
from services.huggingface import query_model

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_message(body: ChatMessage, user: dict = Depends(get_current_user)):
    """Send a message to the AI and get a response."""
    
    # Get or create conversation
    if body.conversation_id:
        conv = await conversations_collection.find_one({
            "_id": ObjectId(body.conversation_id),
            "user_id": user["id"]
        })
    else:
        conv = None
    
    # Query the AI model
    ai_reply = await query_model(body.message)
    
    message_pair = {
        "user": body.message,
        "assistant": ai_reply,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if conv:
        # Append to existing conversation
        await conversations_collection.update_one(
            {"_id": ObjectId(body.conversation_id)},
            {"$push": {"messages": message_pair}}
        )
        conv_id = body.conversation_id
    else:
        # Create new conversation
        new_conv = {
            "user_id": user["id"],
            "title": body.message[:60],
            "messages": [message_pair],
            "created_at": datetime.utcnow().isoformat()
        }
        result = await conversations_collection.insert_one(new_conv)
        conv_id = str(result.inserted_id)
    
    return ChatResponse(reply=ai_reply, conversation_id=conv_id)


@router.get("/history")
async def get_conversations(user: dict = Depends(get_current_user)):
    """Get all conversations for the current user."""
    cursor = conversations_collection.find(
        {"user_id": user["id"]},
        {"messages": {"$slice": -1}, "title": 1, "created_at": 1}
    ).sort("created_at", -1).limit(20)
    
    conversations = []
    async for conv in cursor:
        conversations.append({
            "id": str(conv["_id"]),
            "title": conv.get("title", "Untitled"),
            "last_message": conv["messages"][-1]["assistant"][:100] if conv.get("messages") else "",
            "created_at": conv.get("created_at", "")
        })
    
    return {"conversations": conversations}
