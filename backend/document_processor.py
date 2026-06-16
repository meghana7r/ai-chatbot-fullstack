from PyPDF2 import PdfReader
import os


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    try:
        pdf_reader = PdfReader(file_path)
        print(f"PDF loaded. Total pages: {len(pdf_reader.pages)}")
        
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text


def split_into_chunks(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks"""
    chunks = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():  # only add non-empty chunks
            chunks.append(chunk)
    
    return chunks
