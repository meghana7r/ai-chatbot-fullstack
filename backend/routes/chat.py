from fastapi import APIRouter
from pydantic import BaseModel
import time
from chatbot_engine import get_response

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    source: str
    timestamp: float
    status: str


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

    result = get_response(user_message)

    return ChatResponse(
        response=result["response"],
        source=result["source"],
        timestamp=time.time(),
        status="success"
    )
