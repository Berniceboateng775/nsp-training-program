"""Chat API routes — powers the Vellichor AI chatbot with FAISS retrieval."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from datetime import datetime
from bson import ObjectId
import logging

from auth import get_current_user
from models import ChatMessage, ChatResponse, FileUploadResponse
from database import conversations_collection
from services.huggingface import query_model
from services.pdf_processor import (
    process_document, retrieve_context, session_exists
)
from services.nlp_models import analyze_sentiment, analyze_emotions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_message(body: ChatMessage, user: dict = Depends(get_current_user)):
    """
    Send a message to the AI and get a response.
    If the user has uploaded a document, retrieves relevant chunks
    from FAISS to provide context for the AI response.
    """
    user_id = user["id"]

    # Get or create conversation
    if body.conversation_id:
        conv = await conversations_collection.find_one({
            "_id": ObjectId(body.conversation_id),
            "user_id": user_id
        })
    else:
        conv = None

    # Check if user has a document indexed — retrieve relevant context
    context_chunks = []
    if session_exists(user_id):
        results = retrieve_context(user_id, body.message, top_k=3)
        context_chunks = [r["chunk"] for r in results]

    # Build the prompt with context if available
    if context_chunks:
        context_text = "\n\n---\n\n".join(context_chunks)
        enhanced_prompt = (
            f"Based on the following relevant passages from the user's document:\n\n"
            f"{context_text}\n\n"
            f"---\n\n"
            f"User question: {body.message}\n\n"
            f"Please provide a helpful, detailed answer based on the document content above."
        )
        ai_reply = await query_model(enhanced_prompt)
    else:
        ai_reply = await query_model(body.message)

    # Optionally analyze sentiment of user message
    try:
        msg_sentiment = analyze_sentiment(body.message)
    except Exception:
        msg_sentiment = None

    message_pair = {
        "user": body.message,
        "assistant": ai_reply,
        "timestamp": datetime.utcnow().isoformat(),
        "sentiment": msg_sentiment
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
            "user_id": user_id,
            "title": body.message[:60],
            "messages": [message_pair],
            "created_at": datetime.utcnow().isoformat()
        }
        result = await conversations_collection.insert_one(new_conv)
        conv_id = str(result.inserted_id)

    return ChatResponse(reply=ai_reply, conversation_id=conv_id)


@router.post("/upload", response_model=FileUploadResponse)
async def upload_chat_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    Upload a PDF/TXT to index with FAISS for context-aware chat.
    After uploading, the chatbot can answer questions about the document.
    """
    filename = file.filename or "unknown"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ("pdf", "txt", "text"):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or TXT.")

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    try:
        session_id = user["id"]
        result = process_document(session_id, content, filename)
        return FileUploadResponse(**result)
    except Exception as e:
        logger.error(f"Chat upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


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
