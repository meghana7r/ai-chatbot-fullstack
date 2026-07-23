from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import time
from rag_engine import rag_answer

router = APIRouter()


class Message(BaseModel):
    role: str        # "user" or "bot"
    content: str
    timestamp: Optional[float] = None


class ChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    used_rag: bool
    chunks_retrieved: int
    timestamp: float
    status: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    RAG-powered chat endpoint.
    1. Retrieves relevant chunks from FAISS
    2. Sends query + context to Groq LLM
    3. Returns AI answer with source info
    """
    user_message = request.message.strip()

    if not user_message:
        return ChatResponse(
            response="Please type a message!",
            sources=[],
            used_rag=False,
            chunks_retrieved=0,
            timestamp=time.time(),
            status="error"
        )

    history = [m.model_dump() for m in request.chat_history]
    result = rag_answer(user_message, chat_history=history)

    return ChatResponse(
        response=result["answer"],
        sources=result["sources"],
        used_rag=result["used_rag"],
        chunks_retrieved=result["chunks_retrieved"],
        timestamp=time.time(),
        status="success"
    )


@router.delete("/chat/clear")
def clear_chat():
    return {"message": "Chat cleared!", "status": "success"}
