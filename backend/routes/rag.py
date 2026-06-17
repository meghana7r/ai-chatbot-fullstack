from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from rag_engine import RAGEngine
from document_processor import extract_text

router = APIRouter()

# Global RAG instance
rag = RAGEngine()
UPLOAD_FOLDER = "uploaded_documents"

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process PDF, DOCX, or TXT file"""
    
    try:
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Validate file type
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF, DOCX, and TXT files allowed. Got: {file_ext}"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"✓ File saved: {file_path}")
        
        # Load into RAG
        rag.load_pdf(file_path, doc_name=file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_type": file_ext,
            "message": f"Document uploaded and indexed! Total chunks: {len(rag.chunks)}"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_rag(query: str):
    """Search document with RAG + Groq AI answer"""
    
    try:
        if not rag.index:
            raise HTTPException(
                status_code=400, 
                detail="No document loaded. Please upload a file first (PDF, DOCX, or TXT)."
            )
        
        # Get answer from Groq using document context
        answer = rag.rag_answer(query)
        
        return {
            "status": "success",
            "query": query,
            "answer": answer,
            "source": "rag + groq"
        }
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
