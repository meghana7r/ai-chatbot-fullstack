from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from document_processor import extract_text_from_pdf, split_into_chunks
from groq import Groq
import os

class RAGEngine:
    
    def __init__(self):
        """Initialize RAG with embedding model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.document_name = None
        self.client = None
        print("✓ RAG Engine initialized")
    
    
    def get_groq_client(self):
        """Lazy load Groq client"""
        if self.client is None:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self.client
    
    
    def load_pdf(self, file_path, doc_name="document"):
        """Load PDF and create FAISS index"""
        text = extract_text_from_pdf(file_path)
        print(f"✓ Text extracted: {len(text)} characters")
        
        self.chunks = split_into_chunks(text)
        print(f"✓ Split into {len(self.chunks)} chunks")
        
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        print(f"✓ Embeddings created")
        
        embeddings = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        print(f"✓ FAISS index built with {len(self.chunks)} vectors")
        
        self.document_name = doc_name
    
    
    def search(self, query, top_k=3):
        """Search for similar chunks"""
        if self.index is None:
            return []
        
        query_embedding = self.model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for idx in indices[0]:
            results.append(self.chunks[idx])
        
        return results
    
    
    def rag_answer(self, query):
        """Get answer from Groq using document context"""
        if self.index is None:
            return None
        
        relevant_chunks = self.search(query, top_k=3)
        
        if not relevant_chunks:
            return None
        
        context = "\n".join(relevant_chunks)
        
        client = self.get_groq_client()
        
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful assistant. Use this document information to answer questions:\n\n{context}"
            },
            {
                "role": "user",
                "content": query
            }
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        
        return response.choices[0].message.content
