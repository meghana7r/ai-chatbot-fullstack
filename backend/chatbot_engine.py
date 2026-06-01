import os
import re
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET
from nlp_processor import preprocess

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def keyword_match(original_message: str, processed_message: str):
    """
    Match user message with Q&A dataset.
    Uses BOTH original and processed message for better matching!
    """
    original_lower = original_message.lower().strip()
    processed_lower = processed_message.lower().strip()

    best_match = None
    best_score = 0

    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            keyword_lower = keyword.lower()

            # Check in original message
            pattern = r'\b' + re.escape(keyword_lower) + r'\b'
            if re.search(pattern, original_lower):
                score += 2  # higher score for original match

            # Check in processed message
            elif re.search(pattern, processed_lower):
                score += 1  # lower score for processed match

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score > 0:
        return best_match["response"]

    return None


def ask_groq(user_message: str) -> str:
    """
    Ask Groq AI when no keyword match found.
    """
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
    """
    Main chatbot function:
    1. Run NLP preprocessing on user message
    2. Try keyword matching with processed text
    3. If no match → ask Groq AI
    """
    # Step 1: Run NLP pipeline
    nlp_result = preprocess(user_message)
    processed_message = nlp_result["processed_text"]

    # Step 2: Try keyword matching
    keyword_response = keyword_match(user_message, processed_message)

    if keyword_response:
        return {
            "response": keyword_response,
            "source": "keyword_match"
        }
    else:
        # Step 3: Ask Groq AI
        ai_response = ask_groq(user_message)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }
