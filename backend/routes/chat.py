from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message.strip()

    if not user_message:
        return {
            "user_message": "",
            "bot_reply": "Please enter a message."
        }

    lower_message = user_message.lower()

    if "hello" in lower_message or "hi" in lower_message:
        reply = "Hello! How can I help you today?"
    elif "how are you" in lower_message:
        reply = "I am doing well! How can I assist you?"
    elif "your name" in lower_message:
        reply = "I am your AI chatbot assistant."
    elif "thankyou" in lower_message:
        reply = "You're welcome!"
    else:
        reply = f"You said: {user_message}"

    return {
    "status": "success",
    "user_message": user_message,
    "bot_reply": reply
}