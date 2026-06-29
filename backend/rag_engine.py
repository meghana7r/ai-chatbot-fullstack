from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from groq import Groq
import os

class RAGEngine:
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Store multiple documents
        self.documents = {}  # {filename: {index, chunks, embeddings}}
        self.current_document = None  # Currently selected document
        self.client = None
    
    
    def get_groq_client(self):
        """Lazy load Groq client"""
        if self.client is None:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        return self.client
    
    
    def load_pdf(self, file_path, doc_name="document"):
        """Load PDF and store in documents dictionary"""
        from document_processor import extract_text, split_into_chunks
        
        # Step 1: Extract text
        text = extract_text(file_path)
        
        # Step 2: Split into chunks
        chunks = split_into_chunks(text)
        
        # Step 3: Generate embeddings
        embeddings = self.model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Step 4: Create FAISS index
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        
        # Step 5: Store in documents dictionary
        self.documents[doc_name] = {
            'index': index,
            'chunks': chunks,
            'embeddings': embeddings,
            'file_path': file_path
        }
        
        # Step 6: Set as current document
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
        
        # If deleted current document, switch to another or None
        if self.current_document == doc_name:
            if self.documents:
                self.current_document = list(self.documents.keys())[0]
            else:
                self.current_document = None
        
        return True
    
    
    def search(self, query, top_k=3):
        """Search in current document"""
        if self.current_document is None:
            return []
        
        if self.current_document not in self.documents:
            return []
        
        doc = self.documents[self.current_document]
        index = doc['index']
        chunks = doc['chunks']
        
        # Convert query to embedding
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search FAISS
        distances, indices = index.search(query_embedding, top_k)
        
        # Retrieve actual chunks
        results = []
        for idx in indices[0]:
            results.append(chunks[idx])
        
        return results
    
    
    def search_all_documents(self, query, top_k=3):
        """Search across all documents"""
        all_results = {}
        
        for doc_name in self.documents.keys():
            doc = self.documents[doc_name]
            index = doc['index']
            chunks = doc['chunks']
            
            # Convert query to embedding
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search FAISS
            distances, indices = index.search(query_embedding, top_k)
            
            # Retrieve chunks
            results = []
            for idx in indices[0]:
                results.append(chunks[idx])
            
            all_results[doc_name] = results
        
        return all_results
    
    
    def rag_answer(self, query, use_all_docs=False):
        """Generate answer using RAG"""
        if self.current_document is None and not use_all_docs:
            return None
        
        if use_all_docs:
            # Search all documents
            all_results = self.search_all_documents(query, top_k=2)
            
            if not all_results:
                return None
            
            # Combine results from all documents
            context_parts = []
            for doc_name, chunks in all_results.items():
                if chunks:
                    context_parts.append(f"From {doc_name}:\n" + "\n".join(chunks))
            
            context = "\n\n".join(context_parts)
        
        else:
            # Search current document only
            relevant_chunks = self.search(query, top_k=3)
            
            if not relevant_chunks:
                return None
            
            context = "\n".join(relevant_chunks)
        
        # Send to Groq AI
        client = self.get_groq_client()
        
        messages = [
            {
                "role": "system",
                "content": f"Use this context to answer the question: {context}"
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
