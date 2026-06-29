from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
from chatbot_engine import get_response
from rag_engine import get_rag_engine, clear_rag_session

router = APIRouter()

# ===== DATA MODELS =====

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    session_id: str = "default"

# ===== SETUP =====

UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


# ===== ENDPOINT 1: UPLOAD DOCUMENT =====

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), session_id: str = "default"):
    """Upload a document to a specific chat session"""
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF, DOCX, TXT allowed"
            )
        
        # Get session-specific folder
        session_folder = f"uploaded_documents/{session_id}"
        os.makedirs(session_folder, exist_ok=True)
        
        file_path = os.path.join(session_folder, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Get session's RAG engine
        rag = get_rag_engine(session_id)
        rag.load_pdf(file_path, doc_name=file.filename)
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": f"Document uploaded! Chunks: {len(rag.documents[file.filename]['chunks'])}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 2: CHAT (Session-specific) =====

@router.post("/")
async def chat(request: ChatRequest):
    """
    Chat endpoint - session-specific
    Only sees documents uploaded in this session
    """
    try:
        user_message = request.message.strip()
        session_id = request.session_id or "default"
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        history = []
        for msg in request.history:
            history.append({
                "role": msg.get("role"),
                "content": msg.get("message") or msg.get("content")
            })
        
        # Get session's RAG engine
        rag = get_rag_engine(session_id)
        
        # Get response using session-specific RAG
        result = get_response(user_message, history, rag=rag)
        
        return {
            "status": "success",
            "session_id": session_id,
            "bot_reply": result["response"],
            "source": result.get("source")
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 3: CLEAR SESSION =====

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a chat session and delete all its files"""
    try:
        clear_rag_session(session_id)
        
        return {
            "status": "success",
            "message": f"Session '{session_id}' cleared and files deleted"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 4: LIST DOCUMENTS IN SESSION =====

@router.get("/documents/{session_id}")
async def get_session_documents(session_id: str = "default"):
    """Get all documents in a specific session"""
    try:
        rag = get_rag_engine(session_id)
        documents = rag.get_documents_list()
        
        return {
            "status": "success",
            "session_id": session_id,
            "total_documents": len(documents),
            "documents": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
