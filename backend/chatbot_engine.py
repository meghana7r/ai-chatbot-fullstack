import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET
from nlp_processor import preprocess
from ml_matcher import ml_match

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

WORD_LIMIT = 3


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
    """
    Main chatbot function:
    1. Run NLP preprocessing
    2. Try ML matching using TF-IDF + Cosine Similarity
    3. If no match → ask Groq AI
    """
    # Step 1: Run NLP preprocessing
    nlp_result = preprocess(user_message)
    processed_message = nlp_result["processed_text"]

    word_count = len(user_message.strip().split())

    # Step 2: If has chat history → Groq AI for context
    if len(chat_history) > 0:
        ai_response = ask_groq(user_message, chat_history)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }

    # Step 3: Try ML matching with TF-IDF + Cosine Similarity
    ml_result = ml_match(processed_message)

    if ml_result:
        return {
            "response": ml_result["response"],
            "source": "ml_match",
            "score": ml_result["score"],
            "matched": ml_result["matched_question"]
        }

    # Step 4: No match → Groq AI
    ai_response = ask_groq(user_message, chat_history)
    return {
        "response": ai_response,
        "source": "groq_ai"
    }
