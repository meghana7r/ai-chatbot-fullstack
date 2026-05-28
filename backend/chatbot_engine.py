import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET, DEFAULT_RESPONSE

load_dotenv()

# Connect to Groq AI
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def keyword_match(user_message: str):
    """
    Match user message with Q&A dataset using whole word keyword matching.
    """
    message_lower = user_message.lower().strip()

    best_match = None
    best_score = 0

    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            # Check whole word only — not inside other words!
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, message_lower):
                score += 1

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score > 0:
        return best_match["response"]

    return None


def ask_groq(user_message: str, chat_history: list = []) -> str:
    """
    Ask Groq AI for an answer when no keyword match found.
    """
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer clearly and concisely."
        }
    ]

    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"] if msg["role"] != "bot" else "assistant",
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": user_message})

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content


def get_response(user_message: str, chat_history: list = []) -> dict:
    """
    Main chatbot function:
    1. First try keyword matching
    2. If no match → ask Groq AI
    """
    keyword_response = keyword_match(user_message)

    if keyword_response:
        return {
            "response": keyword_response,
            "source": "keyword_match"
        }
    else:
        ai_response = ask_groq(user_message, chat_history)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }
