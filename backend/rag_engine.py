from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
import os
import shutil
import time
import threading

class RAGEngine:
    
    def __init__(self, session_id=None):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = {}
        self.document_upload_order = []
        self.current_document = None
        self.client = None
        self.relevance_threshold = 0.3
        self.session_id = session_id or "default"
        self.session_folder = f"uploaded_documents/{self.session_id}"
        self.max_documents_per_session = 5
        self.upload_lock = threading.Lock()  # Prevent race conditions
        os.makedirs(self.session_folder, exist_ok=True)
    
    def get_groq_client(self):
        if self.client is None:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self.client
    
    def cleanup_old_documents(self):
        print(f"\n🧹 CLEANUP CHECK: {len(self.documents)}/{self.max_documents_per_session} documents")
        print(f"🧹 Upload order (oldest→newest): {self.document_upload_order}")
        
        while len(self.documents) > self.max_documents_per_session:
            oldest_doc = self.document_upload_order.pop(0)
            print(f"🗑️ REMOVING OLDEST: {oldest_doc}")
            
            if oldest_doc in self.documents:
                file_path = self.documents[oldest_doc].get('file_path')
                
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✓ File deleted from disk: {file_path}")
                
                del self.documents[oldest_doc]
                
                if self.current_document == oldest_doc:
                    if self.documents:
                        self.current_document = self.document_upload_order[-1] if self.document_upload_order else list(self.documents.keys())[0]
                    else:
                        self.current_document = None
        
        print(f"🧹 CLEANUP DONE: {len(self.documents)}/{self.max_documents_per_session}")
        print(f"🧹 Remaining order: {self.document_upload_order}")
    
    def load_pdf(self, file_path, doc_name="document"):
        from document_processor import extract_text, split_into_chunks
        
        # LOCK: Ensure only ONE upload processes at a time per session
        with self.upload_lock:
            print(f"\n🔍 LOADING PDF: {file_path} (timestamp: {time.time()})")
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
                'file_path': file_path,
                'upload_timestamp': time.time()
            }
            
            if doc_name in self.document_upload_order:
                self.document_upload_order.remove(doc_name)
            self.document_upload_order.append(doc_name)
            
            print(f"✓ Upload order NOW: {self.document_upload_order}")
            
            self.cleanup_old_documents()
            
            self.current_document = doc_name
            print(f"✓ Final order: {self.document_upload_order}")
    
    def get_documents_list(self):
        doc_list = []
        for doc_name in self.document_upload_order:
            if doc_name in self.documents:
                doc_list.append({
                    "name": doc_name,
                    "chunks": len(self.documents[doc_name]['chunks']),
                    "is_current": doc_name == self.current_document
                })
        return doc_list
    
    def set_current_document(self, doc_name):
        if doc_name not in self.documents:
            return False
        self.current_document = doc_name
        return True
    
    def delete_document(self, doc_name):
        if doc_name not in self.documents:
            return False
        
        file_path = self.documents[doc_name].get('file_path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        del self.documents[doc_name]
        
        if doc_name in self.document_upload_order:
            self.document_upload_order.remove(doc_name)
        
        if self.current_document == doc_name:
            if self.documents:
                self.current_document = self.document_upload_order[-1] if self.document_upload_order else list(self.documents.keys())[0]
            else:
                self.current_document = None
        
        return True
    
    def clear_session(self):
        for doc_name in list(self.documents.keys()):
            file_path = self.documents[doc_name].get('file_path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        
        self.documents = {}
        self.document_upload_order = []
        self.current_document = None
        
        if os.path.exists(self.session_folder):
            shutil.rmtree(self.session_folder)
            os.makedirs(self.session_folder, exist_ok=True)
        
        print(f"✓ [Session {self.session_id}] Cleared - All files deleted")
    
    def search(self, query, top_k=3):
        if self.current_document is None:
            return [], []
        
        if self.current_document not in self.documents:
            return [], []
        
        doc = self.documents[self.current_document]
        index = doc['index']
        chunks = doc['chunks']
        
        actual_top_k = min(top_k, len(chunks))
        
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        distances, indices = index.search(query_embedding, actual_top_k)
        similarities = 1 / (1 + distances[0][:actual_top_k])
        
        results = []
        scores = []
        for idx, score in zip(indices[0][:actual_top_k], similarities):
            results.append(chunks[idx])
            scores.append(float(score))
        
        return results, scores
    
    def is_relevant(self, scores):
        if not scores:
            return False
        max_score = np.max(scores)
        return max_score >= self.relevance_threshold
    
    def rag_answer(self, query, use_all_docs=False):
        if self.current_document is None and not use_all_docs:
            return None
        
        relevant_chunks, scores = self.search(query, top_k=3)
        
        if not self.is_relevant(scores):
            return None
        
        if not relevant_chunks:
            return None
        
        context = "\n".join(relevant_chunks)
        client = self.get_groq_client()
        
        messages = [
            {"role": "system", "content": f"Use this context to answer: {context}"},
            {"role": "user", "content": query}
        ]
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def has_documents(self):
        return len(self.documents) > 0

rag_engines = {}

def get_rag_engine(session_id="default"):
    if session_id not in rag_engines:
        rag_engines[session_id] = RAGEngine(session_id=session_id)
    return rag_engines[session_id]

def clear_rag_session(session_id):
    if session_id in rag_engines:
        rag_engines[session_id].clear_session()
        del rag_engines[session_id]

def get_all_sessions():
    return list(rag_engines.keys())
