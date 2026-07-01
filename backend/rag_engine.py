from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
import os
import shutil

class RAGEngine:
    
    def __init__(self, session_id=None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = {}
        self.current_document = None
        self.client = None
        self.relevance_threshold = 0.3  # Use max score, so 0.3 is reasonable
        self.session_id = session_id or "default"
        self.session_folder = f"uploaded_documents/{self.session_id}"
        os.makedirs(self.session_folder, exist_ok=True)
    
    
    def get_groq_client(self):
        """Lazy load Groq client"""
        if self.client is None:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self.client
    
    
    def load_pdf(self, file_path, doc_name="document"):
        """Load PDF and store in documents dictionary"""
        from document_processor import extract_text, split_into_chunks
        
        print(f"\n🔍 LOADING PDF: {file_path}")
        text = extract_text(file_path)
        print(f"📄 Extracted text length: {len(text)} characters")
        print(f"📄 First 200 chars: {text[:200]}")
        
        chunks = split_into_chunks(text)
        print(f"📚 Total chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks):
            print(f"   Chunk {i+1}: {len(chunk)} chars - {chunk[:100]}")
        
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
        print(f"✓ [Session {self.session_id}] Document '{doc_name}' loaded with {len(chunks)} chunks")
    
    
    def get_documents_list(self):
        """Get list of all uploaded documents in this session"""
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
        """Delete a document from this session"""
        if doc_name not in self.documents:
            return False
        
        del self.documents[doc_name]
        
        if self.current_document == doc_name:
            if self.documents:
                self.current_document = list(self.documents.keys())[0]
            else:
                self.current_document = None
        
        return True
    
    
    def clear_session(self):
        """Delete all documents and files for this session"""
        self.documents = {}
        self.current_document = None
        
        if os.path.exists(self.session_folder):
            shutil.rmtree(self.session_folder)
            os.makedirs(self.session_folder, exist_ok=True)
        
        print(f"✓ [Session {self.session_id}] Cleared - All files deleted")
    
    
    def search(self, query, top_k=3):
        """Search in current document with relevance scores"""
        print(f"\n🔎 SEARCHING: '{query}'")
        
        if self.current_document is None:
            print("⚠ No current document")
            return [], []
        
        if self.current_document not in self.documents:
            print("⚠ Document not found in registry")
            return [], []
        
        doc = self.documents[self.current_document]
        index = doc['index']
        chunks = doc['chunks']
        
        print(f"📚 Searching in {len(chunks)} chunks")
        
        # Adjust top_k to actual number of chunks
        actual_top_k = min(top_k, len(chunks))
        
        # Convert query to embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS
        distances, indices = index.search(query_embedding, actual_top_k)
        
        print(f"🔍 Raw distances: {distances[0][:actual_top_k]}")
        
        # Convert distances to similarity scores
        similarities = 1 / (1 + distances[0][:actual_top_k])
        
        print(f"📊 Similarity scores: {similarities}")
        
        # Retrieve chunks with scores
        results = []
        scores = []
        for idx, score in zip(indices[0][:actual_top_k], similarities):
            results.append(chunks[idx])
            scores.append(float(score))
            print(f"   Chunk {idx}: score={score:.3f}, text={chunks[idx][:100]}")
        
        return results, scores
    
    
    def is_relevant(self, scores):
        """Check if search results are relevant enough (use MAX score)"""
        if not scores:
            return False
        
        # Use MAX score instead of average
        # This way, if ANY chunk is relevant, we use RAG
        max_score = np.max(scores)
        print(f"📈 Max relevance score: {max_score:.3f}")
        print(f"📈 Threshold: {self.relevance_threshold}")
        
        is_rel = max_score >= self.relevance_threshold
        print(f"📈 Is relevant: {is_rel}")
        
        return is_rel
    
    
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
            
            # Check relevance threshold (using MAX score)
            if not self.is_relevant(scores):
                print(f"⚠ [Session {self.session_id}] Low relevance, using Groq AI instead")
                return None
            
            if not relevant_chunks:
                return None
            
            context = "\n".join(relevant_chunks)
        
        # Send to Groq AI with context
        print(f"✓ Using RAG with context")
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
        """Check if any documents loaded in this session"""
        return len(self.documents) > 0


# Store RAG engines per session
rag_engines = {}

def get_rag_engine(session_id="default"):
    """Get or create RAG engine for session"""
    if session_id not in rag_engines:
        rag_engines[session_id] = RAGEngine(session_id=session_id)
    return rag_engines[session_id]

def clear_rag_session(session_id):
    """Clear a session and delete files"""
    if session_id in rag_engines:
        rag_engines[session_id].clear_session()
        del rag_engines[session_id]

def get_all_sessions():
    """Get all active sessions"""
    return list(rag_engines.keys())
