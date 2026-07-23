from fastapi import APIRouter
from rag_engine import get_index_stats

router = APIRouter()

@router.get("/")
def root():
    return {"message": "AI Chatbot RAG API is running!", "status": "ok"}

@router.get("/health")
def health():
    stats = get_index_stats()
    return {
        "status": "healthy",
        "rag_ready": stats["index_ready"],
        "documents_indexed": len(stats["documents"]),
        "total_chunks": stats["total_chunks"]
    }
