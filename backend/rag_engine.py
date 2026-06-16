from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from document_processor import extract_text_from_pdf, split_into_chunks


class RAGEngine:
    
    def __init__(self):
        """Initialize RAG with embedding model"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        print("✓ RAG Engine initialized")
    
    
    def load_pdf(self, file_path):
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
