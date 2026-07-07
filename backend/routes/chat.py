from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
from chatbot_engine import get_response
from rag_engine import get_rag_engine, clear_rag_session
from database import get_db, save_chat_message, get_chat_history_from_db
from auth import get_current_user_optional
from sqlalchemy.orm import Session

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    session_id: str = "default"

UPLOAD_FOLDER = "uploaded_documents"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
MAX_FILE_SIZE = 3 * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), session_id: str = "default"):
    try:
        print(f"\n📤 UPLOADING FILE: {file.filename}, Session: {session_id}")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Only PDF, DOCX, TXT allowed")
        
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: 3MB"
            )
        
        session_folder = f"uploaded_documents/{session_id}"
        os.makedirs(session_folder, exist_ok=True)
        
        file_path = os.path.join(session_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        rag = get_rag_engine(session_id)
        rag.load_pdf(file_path, doc_name=file.filename)
        
        return {
            "status": "success",
            "message": f"Document uploaded! Chunks: {len(rag.documents[file.filename]['chunks'])}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """
    Chat endpoint - now saves messages to database!
    Works for BOTH logged-in users AND guests.
    """
    try:
        user_message = request.message.strip()
        session_id = request.session_id or "default"
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message required")
        
        # Get user_id if logged in, otherwise None (guest)
        user_id = current_user.id if current_user else None
        
        history = []
        for msg in request.history:
            history.append({
                "role": msg.get("role"),
                "content": msg.get("message") or msg.get("content")
            })
        
        rag = get_rag_engine(session_id)
        result = get_response(user_message, history, rag=rag)
        
        # SAVE USER MESSAGE TO DATABASE
        save_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="user",
            message=user_message,
            source=None
        )
        
        # SAVE BOT REPLY TO DATABASE
        save_chat_message(
            db=db,
            user_id=user_id,
            session_id=session_id,
            role="bot",
            message=result["response"],
            source=result.get("source")
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


@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get past chat messages for a session"""
    try:
        user_id = current_user.id if current_user else None
        
        messages = get_chat_history_from_db(db, session_id, user_id)
        
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
