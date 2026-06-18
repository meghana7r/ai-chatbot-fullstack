# SHARED_STATE.PY
# Single RAG instance shared across all endpoints

from rag_engine import RAGEngine

# Create ONE instance
rag = RAGEngine()

# Both routes/rag.py and chatbot_engine.py import this same instance
