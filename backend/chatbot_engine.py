import os
from groq import Groq
from dotenv import load_dotenv
from dataset import QA_DATASET, DEFAULT_RESPONSE

load_dotenv()

# Connect to Groq AI
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def keyword_match(user_message: str):
    """
    Step 1: Try to match user message with our Q&A dataset
    using keyword matching algorithm.
    Returns the matched response or None if no match found.
    """
    message_lower = user_message.lower().strip()

    best_match = None
    best_score = 0

    for qa in QA_DATASET:
        score = 0
        for keyword in qa["keywords"]:
            if keyword.lower() in message_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_match = qa

    if best_match and best_score > 0:
        return best_match["response"]

    return None  # no keyword match found


def ask_groq(user_message: str, chat_history: list = []) -> str:
    """
    Step 2: If no keyword match, ask Groq AI for an answer.
    This is the AI model integration.
    """
    # Build conversation history for context
    messages = [
        {
            "role": "system",
            "content": "You are a helpful and friendly AI assistant. Answer clearly and concisely."
        }
    ]

    # Add last 6 messages for conversation context
    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"] if msg["role"] != "bot" else "assistant",
            "content": msg["content"]
        })

    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Call Groq AI
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
    1. First try keyword matching (rule-based)
    2. If no match → ask Groq AI (AI model)
    """
    # Step 1: Try keyword matching
    keyword_response = keyword_match(user_message)

    if keyword_response:
        # Keyword matched → return dataset answer
        return {
            "response": keyword_response,
            "source": "keyword_match"  # tells us it came from dataset
        }
    else:
        # No keyword match → ask Groq AI
        ai_response = ask_groq(user_message, chat_history)
        return {
            "response": ai_response,
            "source": "groq_ai"  # tells us it came from AI
        }
