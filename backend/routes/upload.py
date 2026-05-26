from fastapi import APIRouter, UploadFile, File, HTTPException
from rag_engine import add_to_faiss, save_index, clear_index, get_index_stats
from document_processor import extract_text
from rag_engine import split_text

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a document → extract text → split into chunks
    → embed with SentenceTransformer → store in FAISS
    """
    # Validate file type
    ext = file.filename.lower().split(".")[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Please upload: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file bytes
    file_bytes = await file.read()

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 10MB.")

    # Extract text from document
    try:
        text = extract_text(file.filename, file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read file: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=422, detail="No text could be extracted from this file.")

    # Split into chunks
    chunks = split_text(text, source=file.filename)

    # Add to FAISS
    add_to_faiss(chunks)

    # Save index to disk
    save_index()

    return {
        "message": f"✅ '{file.filename}' uploaded and indexed successfully!",
        "filename": file.filename,
        "chunks_created": len(chunks),
        "characters_extracted": len(text),
        "status": "success"
    }


@router.get("/upload/stats")
def index_stats():
    """Return info about the current FAISS index."""
    return get_index_stats()


@router.delete("/upload/clear")
def clear_documents():
    """Remove all documents from the FAISS index."""
    clear_index()
    return {"message": "All documents cleared from index.", "status": "success"}
