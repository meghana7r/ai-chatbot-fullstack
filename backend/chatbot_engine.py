import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def keyword_match(user_message: str):
    message_lower = user_message.lower().strip()

    best_match = None
    best_score = 0

    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, message_lower):
                score += 1

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score > 0:
        return best_match["response"]

    return None


def ask_groq(user_message: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer clearly and concisely."
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content


def get_response(user_message: str) -> dict:
    keyword_response = keyword_match(user_message)

    if keyword_response:
        return {
            "response": keyword_response,
            "source": "keyword_match"
        }
    else:
        ai_response = ask_groq(user_message)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }
