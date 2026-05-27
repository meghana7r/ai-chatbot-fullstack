from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import time
from chatbot_engine import get_response

router = APIRouter()


# ── Request Model (what frontend sends) ──────────────────────────────────────
class Message(BaseModel):
    role: str        # "user" or "bot"
    content: str


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Message]] = []


# ── Response Model (what backend returns) ─────────────────────────────────────
class ChatResponse(BaseModel):
    response: str
    source: str      # "keyword_match" or "groq_ai"
    timestamp: float
    status: str


# ── Chat Endpoint ─────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Main chat endpoint.
    1. Receives user message
    2. Tries keyword matching first
    3. Falls back to Groq AI if no keyword match
    4. Returns the response
    """
    user_message = request.message.strip()

    if not user_message:
        return ChatResponse(
            response="Please type a message!",
            source="error",
            timestamp=time.time(),
            status="error"
        )

    # Convert chat history to list of dicts
    history = [m.model_dump() for m in request.chat_history]

    # Get response from chatbot engine
    result = get_response(user_message, chat_history=history)

    return ChatResponse(
        response=result["response"],
        source=result["source"],
        timestamp=time.time(),
        status="success"
    )


# ── Clear Chat ────────────────────────────────────────────────────────────────
@router.delete("/chat/clear")
def clear_chat():
    return {"message": "Chat cleared successfully!", "status": "success"}


# ── Chat History (placeholder for future weeks) ───────────────────────────────
@router.get("/chat/history")
def get_history():
    return {
        "history": [],
        "message": "Chat history with database coming in Week 3!"
    }
