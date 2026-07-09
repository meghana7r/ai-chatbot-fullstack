from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from pydantic import BaseModel, field_validator
from typing import List, Optional
import os
import re
from chatbot_engine import get_response
from rag_engine import get_rag_engine, clear_rag_session
from database import get_db, save_chat_message, get_chat_history_from_db
from auth import get_current_user_optional
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# ===== VALIDATED SCHEMAS =====

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    session_id: str = "default"
    
    @field_validator('message')
    @classmethod
    def message_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 2000:
            raise ValueError('Message too long (max 2000 characters)')
        return v.strip()
    
    @field_validator('session_id')
    @classmethod
    def session_id_must_be_valid(cls, v):
        if not v or not v.strip():
            return "default"
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Session ID can only contain letters, numbers, underscore, hyphen')
        if len(v) > 100:
            raise ValueError('Session ID too long (max 100 characters)')
        return v


UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 3 * 1024 * 1024


# ===== ENDPOINT 1: UPLOAD DOCUMENT (Rate limited: 10 uploads per minute) =====

@router.post("/upload")
@limiter.limit("10/minute")
async def upload_document(request: Request, file: UploadFile = File(...), session_id: str = "default"):
    try:
        if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Only PDF, DOCX, TXT allowed. Got: {file_ext}")
        
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File too large. Max size: 3MB")
        
        session_folder = f"uploaded_documents/{session_id}"
        os.makedirs(session_folder, exist_ok=True)
        
        safe_filename = re.sub(r'[^\w\s.-]', '', file.filename)
        
        file_path = os.path.join(session_folder, safe_filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        rag = get_rag_engine(session_id)
        rag.load_pdf(file_path, doc_name=safe_filename)
        
        return {
            "status": "success",
            "message": f"Document uploaded! Chunks: {len(rag.documents[safe_filename]['chunks'])}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 2: CHAT (Rate limited: 30 messages per minute) =====

@router.post("/")
@limiter.limit("30/minute")
async def chat(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    try:
        user_message = chat_request.message
        session_id = chat_request.session_id
        
        user_id = current_user.id if current_user else None
        
        history = []
        for msg in chat_request.history:
            history.append({
                "role": msg.get("role"),
                "content": msg.get("message") or msg.get("content")
            })
        
        rag = get_rag_engine(session_id)
        result = get_response(user_message, history, rag=rag)
        
        save_chat_message(
            db=db, user_id=user_id, session_id=session_id,
            role="user", message=user_message, source=None
        )
        
        save_chat_message(
            db=db, user_id=user_id, session_id=session_id,
            role="bot", message=result["response"], source=result.get("source")
        )
        
        return {
            "status": "success",
            "bot_reply": result["response"],
            "source": result.get("source"),
            "logged_in": current_user is not None
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 3: GET CHAT HISTORY (Ownership check added) =====

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    try:
        user_id = current_user.id if current_user else None
        messages = get_chat_history_from_db(db, session_id, user_id)
        
        # Security: If user is logged in, only show messages that either 
        # belong to them OR are guest messages (user_id=None) for this session
        # This prevents User A from viewing User B's saved history in the same session_id
        
        history_list = []
        for msg in messages:
            history_list.append({
                "role": msg.role,
                "message": msg.message,
                "source": msg.source,
                "timestamp": msg.timestamp.isoformat()
            })
        
        return {
            "status": "success",
            "session_id": session_id,
            "total_messages": len(history_list),
            "history": history_list
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{session_id}")
async def get_session_documents(session_id: str):
    try:
        rag = get_rag_engine(session_id)
        documents = rag.get_documents_list()
        
        return {
            "status": "success",
            "session_id": session_id,
            "total_documents": len(documents),
            "current_document": rag.current_document,
            "documents": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-file/{session_id}/{doc_name}")
async def delete_file_endpoint(session_id: str, doc_name: str):
    try:
        rag = get_rag_engine(session_id)
        success = rag.delete_document(doc_name)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"File '{doc_name}' not found")
        
        return {
            "status": "success",
            "message": f"File '{doc_name}' deleted successfully",
            "remaining_documents": len(rag.documents),
            "current_document": rag.current_document
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-session/{session_id}")
async def clear_session_endpoint(session_id: str):
    try:
        clear_rag_session(session_id)
        return {"status": "success", "message": f"Session '{session_id}' cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
