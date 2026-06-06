# routes/chat.py — MegaBot Chat Route
# Built by Meghana Ravi
# This file handles the /chat endpoint and connects to Groq AI (Llama 3)
# Updated to send full conversation history so MegaBot remembers context!

from fastapi import APIRouter
from pydantic import BaseModel, Field
from datetime import datetime
import os
from groq import Groq
from dotenv import load_dotenv

# Load the .env file to get the GROQ_API_KEY
load_dotenv()

router = APIRouter()

# Connect to Groq using the API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Shape of each message in the history list
class HistoryMessage(BaseModel):
    role: str      # "user" or "bot"
    message: str   # the actual message text

# Shape of the request body — message + full conversation history
class ChatRequest(BaseModel):
    message: str = Field(..., example="Hello AI")
    history: list[HistoryMessage] = []  # previous messages for context

@router.post(
    "/chat",
    summary="Chatbot Communication API",
    description="Receives user message and returns Groq AI response"
)
def chat(request: ChatRequest):
    user_message = request.message.strip()

    if not user_message:
        return {"bot_reply": "Please type a message!", "status": "error"}

    try:
        # Build conversation history for Groq
        # This is what makes MegaBot remember previous messages!
        conversation = [
            {
                "role": "system",
                "content": "You are MegaBot, a smart and friendly AI assistant built by Meghana Ravi. Keep replies concise and helpful."
            },
            # Add all previous messages so Groq has full context
            *[
                {
                    "role": "user" if m.role == "user" else "assistant",
                    "content": m.message
                }
                for m in request.history
            ],
            # Add the current new message at the end
            {
                "role": "user",
                "content": user_message
            }
        ]

        # Send full conversation to Groq Llama 3
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation,
            max_tokens=500,
        )

        # Extract the reply text from Groq response
        bot_reply = completion.choices[0].message.content

    except Exception as e:
        bot_reply = f"Sorry, I could not get a response from the AI. Please try again."

    return {
        "status": "success",
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "user_message": user_message,
        "bot_reply": bot_reply
    }
