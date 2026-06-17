import os
from nlp_processor import preprocess
from ml_matcher import ml_match
from groq import Groq
from rag_engine import RAGEngine

rag = RAGEngine()

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(user_message, chat_history=[]):
    nlp = preprocess(user_message)
    processed_message = nlp['processed_text']
    
    has_document = rag.index is not None
    
    ml_result = ml_match(processed_message)
    
    if ml_result:
        return {
            "response": ml_result["response"],
            "source": "ml_match"
        }
    
    if has_document:
        answer = rag.rag_answer(user_message)
        if answer:
            return {
                "response": answer,
                "source": "rag + groq"
            }
    
    answer = ask_groq(user_message, chat_history)
    
    return {
        "response": answer,
        "source": "groq_ai"
    }


def ask_groq(user_message, chat_history=[]):
    client = get_groq_client()
    
    messages = []
    
    messages.append({
        "role": "system",
        "content": "You are a helpful AI assistant for Gaint Clout."
    })
    
    last_10_messages = chat_history[-10:]
    
    for msg in last_10_messages:
        role = "assistant" if msg.get("role") == "bot" else msg.get("role")
        content = msg.get("content") or msg.get("message")
        
        messages.append({
            "role": role,
            "content": content
        })
    
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.7
    )
    
    return response.choices[0].message.content
