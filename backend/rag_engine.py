from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
import os

class RAGEngine:
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = {}
        self.current_document = None
        self.client = None
        self.relevance_threshold = 0.4  # Minimum similarity score (0-1)
    
    
    def get_groq_client(self):
        """Lazy load Groq client"""
        if self.client is None:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self.client
    
    
    def load_pdf(self, file_path, doc_name="document"):
        """Load PDF and store in documents dictionary"""
        from document_processor import extract_text, split_into_chunks
        
        text = extract_text(file_path)
        chunks = split_into_chunks(text)
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        
        self.documents[doc_name] = {
            'index': index,
            'chunks': chunks,
            'embeddings': embeddings,
            'file_path': file_path
        }
        
        self.current_document = doc_name
        print(f"✓ Document '{doc_name}' loaded with {len(chunks)} chunks")
    
    
    def get_documents_list(self):
        """Get list of all uploaded documents"""
        doc_list = []
        for doc_name in self.documents.keys():
            doc_list.append({
                "name": doc_name,
                "chunks": len(self.documents[doc_name]['chunks']),
                "is_current": doc_name == self.current_document
            })
        return doc_list
    
    
    def set_current_document(self, doc_name):
        """Switch to a different document"""
        if doc_name not in self.documents:
            return False
        self.current_document = doc_name
        return True
    
    
    def delete_document(self, doc_name):
        """Delete a document"""
        if doc_name not in self.documents:
            return False
        
        del self.documents[doc_name]
        
        if self.current_document == doc_name:
            if self.documents:
                self.current_document = list(self.documents.keys())[0]
            else:
                self.current_document = None
        
        return True
    
    
    def search(self, query, top_k=3):
        """Search in current document with relevance scores"""
        if self.current_document is None:
            return [], []
        
        if self.current_document not in self.documents:
            return [], []
        
        doc = self.documents[self.current_document]
        index = doc['index']
        chunks = doc['chunks']
        
        # Convert query to embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS
        distances, indices = index.search(query_embedding, top_k)
        
        # Convert distances to similarity scores (0-1, higher = more similar)
        # FAISS returns L2 distances, convert to similarity
        similarities = 1 / (1 + distances[0])  # Inverse distance = similarity
        
        # Retrieve chunks with scores
        results = []
        scores = []
        for idx, score in zip(indices[0], similarities):
            results.append(chunks[idx])
            scores.append(float(score))
        
        return results, scores
    
    
    def is_relevant(self, scores):
        """Check if search results are relevant enough"""
        if not scores:
            return False
        
        # Average similarity score
        avg_score = np.mean(scores)
        
        # Return True if above threshold
        return avg_score >= self.relevance_threshold
    
    
    def rag_answer(self, query, use_all_docs=False):
        """Generate answer using RAG only if relevant"""
        if self.current_document is None and not use_all_docs:
            return None
        
        if use_all_docs:
            all_results = {}
            for doc_name in self.documents.keys():
                doc = self.documents[doc_name]
                index = doc['index']
                chunks = doc['chunks']
                
                query_embedding = self.model.encode([query])
                query_embedding = np.array(query_embedding).astype('float32')
                distances, indices = index.search(query_embedding, top_k=2)
                similarities = 1 / (1 + distances[0])
                
                results = []
                for idx in indices[0]:
                    results.append(chunks[idx])
                
                all_results[doc_name] = results
            
            if not all_results:
                return None
            
            context_parts = []
            for doc_name, chunks in all_results.items():
                if chunks:
                    context_parts.append(f"From {doc_name}:\n" + "\n".join(chunks))
            
            context = "\n\n".join(context_parts)
        
        else:
            # Search in current document
            relevant_chunks, scores = self.search(query, top_k=3)
            
            # Check relevance threshold
            if not self.is_relevant(scores):
                print(f"⚠ Low relevance (avg: {np.mean(scores):.2f}), using Groq AI instead")
                return None  # Fall back to Groq
            
            if not relevant_chunks:
                return None
            
            context = "\n".join(relevant_chunks)
        
        # Send to Groq AI with context
        client = self.get_groq_client()
        
        messages = [
            {
                "role": "system",
                "content": f"Use this context to answer: {context}"
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
    
    
    def has_documents(self):
        """Check if any documents loaded"""
        return len(self.documents) > 0


# Singleton RAG instance shared across all endpoints
rag = RAGEngine()
