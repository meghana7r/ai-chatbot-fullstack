from fastapi import APIRouter

router = APIRouter()

@router.get("/info")
def get_chatbot_info():
    return {
        "name": "AI Chatbot",
        "version": "1.0.0",
        "description": "An intelligent conversational chatbot that uses AI to answer your questions smartly and accurately.",
        "what_can_it_do": [
            "Answer general knowledge questions",
            "Have friendly conversations",
            "Respond to greetings and casual chat",
            "Answer questions about AI, Python, Data Science",
            "Tell jokes",
            "Provide study resources"
        ],
        "specialities": [
            "Uses Groq Llama 3 AI model for smart responses",
            "Keyword matching for instant replies",
            "Falls back to AI when no keyword match found",
            "Fast and accurate responses",
            "Friendly and conversational tone"
        ],
        "technology": {
            "backend": "Python FastAPI",
            "frontend": "React Next.js",
            "ai_model": "Groq Llama 3.3 70B",
            "algorithm": "Keyword Matching + AI Fallback"
        },
        "developers": {
            "backend": "Amrutha Varshini",
            "frontend": "Meghana Ravi"
        }
    }
