import os
from nlp_processor import preprocess
from ml_matcher import ml_match
from groq import Groq, APIError, APITimeoutError, RateLimitError
from logger_config import logger

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(user_message, chat_history=[], rag=None):
    """Get response using session-specific RAG"""
    try:
        nlp = preprocess(user_message)
        processed_message = nlp['processed_text']
        
        has_documents = rag.has_documents() if rag else False
        
        # PRIORITY 1: ML Match (Dataset)
        ml_result = ml_match(processed_message)
        
        if ml_result:
            return {
                "response": ml_result["response"],
                "source": "ml_match"
            }
        
        # PRIORITY 2: RAG (If documents loaded)
        if has_documents:
            try:
                answer = rag.rag_answer(user_message, use_all_docs=False)
                if answer:
                    return {
                        "response": answer,
                        "source": "rag + groq"
                    }
            except Exception as e:
                logger.error(f"RAG search failed: {str(e)}", exc_info=True)
                # Fall through to Groq fallback below
        
        # PRIORITY 3: Fallback to Groq
        answer = ask_groq(user_message, chat_history)
        
        return {
            "response": answer,
            "source": "groq_ai"
        }
    
    except Exception as e:
        logger.error(f"get_response failed completely: {str(e)}", exc_info=True)
        return {
            "response": "I'm having trouble processing your request right now. Please try again in a moment.",
            "source": "error"
        }


def ask_groq(user_message, chat_history=[]):
    try:
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
            
            if content:  # Skip empty messages
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
            temperature=0.7,
            timeout=30  # 30 second timeout
        )
        
        return response.choices[0].message.content
    
    except RateLimitError:
        logger.error("Groq API rate limit exceeded")
        return "I'm receiving too many requests right now. Please try again in a minute."
    
    except APITimeoutError:
        logger.error("Groq API timeout")
        return "The request took too long to process. Please try again."
    
    except APIError as e:
        logger.error(f"Groq API error: {str(e)}")
        return "I'm having trouble connecting to my AI service. Please try again shortly."
    
    except Exception as e:
        logger.error(f"Unexpected error in ask_groq: {str(e)}", exc_info=True)
        return "Something unexpected happened. Please try again."
