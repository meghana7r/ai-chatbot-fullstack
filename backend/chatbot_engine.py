import os
from groq import Groq
from dotenv import load_dotenv
from nlp_processor import preprocess
from ml_matcher import ml_match

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


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
    Main chatbot function - Method 3:
    1. Run NLP preprocessing FIRST
    2. Try ML match with processed message
    3. If score HIGH (>=0.5) → return dataset answer
    4. If score LOW (<0.5) → send to Groq AI
    """

    # Step 1: NLP preprocessing
    nlp_result = preprocess(user_message)
    processed_message = nlp_result["processed_text"]

    print(f"Original:  {user_message}")
    print(f"Processed: {processed_message}")

    # Step 2: If has chat history → Groq AI for context
    if len(chat_history) > 0:
        ai_response = ask_groq(user_message, chat_history)
        return {
            "response": ai_response,
            "source": "groq_ai"
        }

    # Step 3: Try ML match with PROCESSED message
    ml_result = ml_match(processed_message, threshold=0.5)

    if ml_result:
        print(f"ML match found! Score: {ml_result['score']:.2f}")
        return {
            "response": ml_result["response"],
            "source": "ml_match",
            "score": ml_result["score"],
            "matched": ml_result["matched_question"]
        }

    # Step 4: Score too low → Groq AI
    print(f"No good ML match → Groq AI")
    ai_response = ask_groq(user_message, chat_history)
    return {
        "response": ai_response,
        "source": "groq_ai"
    }
