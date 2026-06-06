import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET
from nlp_processor import preprocess

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

WORD_LIMIT = 3


def keyword_match(original_message: str, processed_message: str):
    original_lower = original_message.lower().strip()
    processed_lower = processed_message.lower().strip()

    best_match = None
    best_score = 0

    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            keyword_lower = keyword.lower()
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            if re.search(pattern, original_lower):
                score += 2
            elif re.search(pattern, processed_lower):
                score += 1

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score > 0:
        return best_match["response"]

    return None


def ask_groq(user_message: str, chat_history: list = []) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer clearly and concisely. Remember the conversation history and reply accordingly."
        }
    ]

    
    for msg in chat_history[-10:]:
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
    nlp_result = preprocess(user_message)
    processed_message = nlp_result["processed_text"]

    word_count = len(user_message.strip().split())

    
    if word_count > WORD_LIMIT or len(chat_history) > 0:
        ai_response = ask_groq(user_message, chat_history)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }

    
    keyword_response = keyword_match(user_message, processed_message)

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
