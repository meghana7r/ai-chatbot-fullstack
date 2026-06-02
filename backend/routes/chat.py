from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import time
from chatbot_engine import get_response

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Message]] = []


@router.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message.strip()

    if not user_message:
        return {"bot_reply": "Please type a message!", "status": "error"}

    history = [m.model_dump() for m in request.chat_history]
    result = get_response(user_message, chat_history=history)

    return {
        "bot_reply": result["response"],   # ← matches Meghana's code!
        "source": result["source"],
        "timestamp": time.time(),
        "status": "success"
    }
