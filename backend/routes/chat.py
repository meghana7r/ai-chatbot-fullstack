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

class ChatResponse(BaseModel):
    response: str
    source: str      
    timestamp: float
    status: str
@router.get("/")
def root():
    return {"message": "AI Chatbot API is running!", "status": "ok"}

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_message = request.message.strip()

    if not user_message:
        return ChatResponse(
            response="Please type a message!",
            source="error",
            timestamp=time.time(),
            status="error"
        )

    history = [m.model_dump() for m in request.chat_history]

    result = get_response(user_message, chat_history=history)

    return ChatResponse(
        response=result["response"],
        source=result["source"],
        timestamp=time.time(),
        status="success"
    )



