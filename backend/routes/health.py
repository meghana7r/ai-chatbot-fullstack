from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"message": "AI Chatbot API is running!", "status": "ok"}


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Chatbot Backend"}
