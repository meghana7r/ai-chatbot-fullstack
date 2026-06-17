from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from chatbot_engine import get_response
from datetime import datetime

router = APIRouter()

class Message(BaseModel):
    role: str
    message: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

@router.post("/")
async def chat(request: ChatRequest):
    """Chat endpoint with ML matching, RAG, and Groq AI"""
    
    user_message = request.message.strip()
    
    if not user_message:
        return {
            "bot_reply": "Please type a message!",
            "source": "error",
            "timestamp": datetime.now().isoformat(),
            "status": "error"
        }
    
    # Convert history format
    history = []
    for msg in request.history:
        history.append({
            "role": msg.role,
            "content": msg.message
        })
    
    # Get response from integrated chatbot engine
    result = get_response(user_message, history)
    
    return {
        "bot_reply": result["response"],
        "source": result["source"],
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }
