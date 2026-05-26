import io
from pypdf import PdfReader
from docx import Document


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Extract raw text from uploaded file.
    Supports: PDF, DOCX, TXT
    """
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        return extract_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_from_docx(file_bytes)
    elif ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: .{ext}. Please upload PDF, DOCX, or TXT.")


def extract_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using pypdf."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_from_docx(file_bytes: bytes) -> str:
    """Extract text from Word document."""
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)
