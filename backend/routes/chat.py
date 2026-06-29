from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
from chatbot_engine import get_response
from rag_engine import rag

router = APIRouter()

# ===== DATA MODELS =====

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

# ===== SETUP =====

UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


# ===== ENDPOINT 1: UPLOAD DOCUMENT =====

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF, DOCX, TXT allowed"
            )
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        rag.load_pdf(file_path, doc_name=file.filename)
        
        return {
            "status": "success",
            "message": f"Document uploaded! Chunks: {len(rag.documents[file.filename]['chunks'])}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 2: CHAT (Handles everything) =====

@router.post("/")
async def chat(request: ChatRequest):
    """
    Universal chat endpoint - handles:
    1. Regular chat messages
    2. RAG search (if document uploaded)
    3. ML matching (if question in dataset)
    4. Groq AI fallback
    """
    try:
        user_message = request.message.strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        history = []
        for msg in request.history:
            history.append({
                "role": msg.get("role"),
                "content": msg.get("message") or msg.get("content")
            })
        
        # This handles ALL logic internally:
        # - ML match
        # - RAG search (if doc loaded)
        # - Groq fallback
        result = get_response(user_message, history)
        
        return {
            "status": "success",
            "bot_reply": result["response"],
            "source": result.get("source")
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
