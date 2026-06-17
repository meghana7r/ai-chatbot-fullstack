from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from document_processor import extract_text_from_pdf, split_into_chunks
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class RAGEngine:
    
    def __init__(self):
        """Initialize RAG with embedding model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.document_name = None
        print("✓ RAG Engine initialized")
    
    
    def load_pdf(self, file_path, doc_name="document"):
        """Load PDF and create FAISS index"""
        # Step 1: Extract text
        text = extract_text_from_pdf(file_path)
        print(f"✓ Text extracted: {len(text)} characters")
        
        # Step 2: Split into chunks
        self.chunks = split_into_chunks(text)
        print(f"✓ Split into {len(self.chunks)} chunks")
        
        # Step 3: Create embeddings
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)
        print(f"✓ Embeddings created")
        
        # Step 4: Build FAISS index
        embeddings = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)
        print(f"✓ FAISS index built with {len(self.chunks)} vectors")
        
        self.document_name = doc_name
    
    
    def search(self, query, top_k=3):
        """Search for similar chunks"""
        if self.index is None:
            return []
        
        # Convert query to embedding
        query_embedding = self.model.encode([query], show_progress_bar=False)
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Return chunks
        results = []
        for idx in indices[0]:
            results.append(self.chunks[idx])
        
        return results
    
    
    def rag_answer(self, query):
        """Get answer from Groq using document context"""
        if self.index is None:
            return "❌ No document loaded"
        
        # Step 1: Search for relevant chunks
        relevant_chunks = self.search(query, top_k=3)
        
        if not relevant_chunks:
            return "No relevant information found in document"
        
        # Step 2: Create context from chunks
        context = "\n".join(relevant_chunks)
        
        # Step 3: Send to Groq
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
