from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat"])

last_user_message = ""


class ChatRequest(BaseModel):
    message: str = Field(..., example="Hello AI")


@router.post(
    "/chat",
    summary="Chatbot Communication API",
    description="Receives user message and returns chatbot response"
)
def chat(request: ChatRequest):
    global last_user_message

    user_message = request.message.strip()
    logger.info(f"User Message: {user_message}")

    if not user_message:
        return {
            "status": "error",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "user_message": "",
            "bot_reply": "Please enter a message."
        }

    lower_message = user_message.lower()

    if "what did i say" in lower_message:
        if last_user_message:
            reply = "I received your message. I am still learning to answer this properly."
        else:
            reply = "I don't remember any previous message yet."

    elif "hello" in lower_message or "hi" in lower_message:
        reply = "Hello! How can I help you today?"

    elif "how are you" in lower_message:
        reply = "I am doing well! How can I assist you?"

    elif "your name" in lower_message:
        reply = "I am your AI chatbot assistant."

    elif "thank" in lower_message:
        reply = "You're welcome!"

    elif "bye" in lower_message:
        reply = "Goodbye! Have a great day!"

    elif "help" in lower_message:
        reply = "I can help answer your questions."

    elif "who created you" in lower_message:
        reply = "I was created as part of an AI chatbot internship project."

    else:
        reply = f"You said: {user_message}"

    if "what did i say" not in lower_message:
        last_user_message = user_message

    time.sleep(1)

    return {
        "status": "success",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "user_message": user_message,
        "bot_reply": reply
    }