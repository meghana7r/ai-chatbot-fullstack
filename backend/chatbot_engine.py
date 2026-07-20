import os
import time
from nlp_processor import preprocess
from ml_matcher import ml_match
from groq import Groq, APIError, APITimeoutError, RateLimitError
from logger_config import logger

def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(user_message, chat_history=[], rag=None):
    start_time = time.time()
    
    try:
        t1 = time.time()
        nlp = preprocess(user_message)
        processed_message = nlp['processed_text']
        print(f"⏱️ NLP preprocessing: {time.time()-t1:.3f}s")
        
        has_documents = rag.has_documents() if rag else False
        
        t2 = time.time()
        ml_result = ml_match(processed_message)
        print(f"⏱️ ML matching: {time.time()-t2:.3f}s")
        
        if ml_result:
            print(f"⏱️ TOTAL TIME: {time.time()-start_time:.3f}s")
            return {
                "response": ml_result["response"],
                "source": "ml_match"
            }
        
        if has_documents:
            try:
                t3 = time.time()
                answer = rag.rag_answer(user_message, use_all_docs=False)
                print(f"⏱️ RAG search + Groq: {time.time()-t3:.3f}s")
                if answer:
                    print(f"⏱️ TOTAL TIME: {time.time()-start_time:.3f}s")
                    return {
                        "response": answer,
                        "source": "rag + groq"
                    }
            except Exception as e:
                logger.error(f"RAG search failed: {str(e)}", exc_info=True)
        
        t4 = time.time()
        answer = ask_groq(user_message, chat_history)
        print(f"⏱️ Groq AI call: {time.time()-t4:.3f}s")
        
        print(f"⏱️ TOTAL TIME: {time.time()-start_time:.3f}s")
        
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
            
            if content:
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
            timeout=30
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
