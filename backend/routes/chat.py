from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message

    return {
        "user_message": user_message,
        "bot_reply": f"You said: {user_message}"
    }