from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
import os
from chatbot_engine import get_response
from rag_engine import get_rag_engine

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
        print(f"\n📤 UPLOADING FILE: {file.filename}, Session: {session_id}")
        
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
        
        print(f"✓ File saved to: {file_path}")
        
        # Get session's RAG engine
        rag = get_rag_engine(session_id)
        print(f"✓ Got RAG engine for session: {session_id}")
        print(f"✓ RAG documents before: {list(rag.documents.keys())}")
        
        rag.load_pdf(file_path, doc_name=file.filename)
        
        print(f"✓ RAG documents after: {list(rag.documents.keys())}")
        print(f"✓ Current document: {rag.current_document}")
        print(f"✓ Has documents: {rag.has_documents()}")
        
        return {
            "status": "success",
            "message": f"Document uploaded! Chunks: {len(rag.documents[file.filename]['chunks'])}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ UPLOAD ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== ENDPOINT 2: CHAT =====

@router.post("/")
async def chat(request: ChatRequest):
    """Chat endpoint - session-specific"""
    try:
        user_message = request.message.strip()
        session_id = request.session_id or "default"
        
        print(f"\n💬 CHAT MESSAGE: {user_message}, Session: {session_id}")
        
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
        
        print(f"✓ Got RAG engine for session: {session_id}")
        print(f"✓ RAG documents: {list(rag.documents.keys())}")
        print(f"✓ Current document: {rag.current_document}")
        print(f"✓ Has documents: {rag.has_documents()}")
        
        if rag.has_documents():
            print(f"✓ WILL TRY RAG")
        else:
            print(f"⚠ NO DOCUMENTS - Will use Groq")
        
        # Get response using session-specific RAG
        result = get_response(user_message, history, rag=rag)
        
        print(f"✓ Response source: {result.get('source')}")
        
        return {
            "status": "success",
            "bot_reply": result["response"],
            "source": result.get("source")
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"❌ CHAT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
