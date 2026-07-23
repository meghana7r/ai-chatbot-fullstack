import os
import faiss
import numpy as np
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

# ── Load models once at startup ──────────────────────────────────────────────
print("Loading embedding model... (first time may take a minute)")
embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-8b-8192")

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# In-memory storage for document chunks (maps FAISS index → text)
document_store = []   # list of {"text": ..., "source": ...}
faiss_index = None    # FAISS index object


# ── 1. Text Splitting ─────────────────────────────────────────────────────────
def split_text(text: str, source: str) -> list[dict]:
    """Split document text into overlapping chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    return [{"text": chunk, "source": source} for chunk in chunks]


# ── 2. Embedding ──────────────────────────────────────────────────────────────
def embed_texts(texts: list[str]) -> np.ndarray:
    """Convert list of strings to embedding vectors."""
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    return embeddings.astype("float32")


# ── 3. Add Document to FAISS ──────────────────────────────────────────────────
def add_to_faiss(chunks: list[dict]):
    """Embed chunks and add to FAISS index."""
    global faiss_index, document_store

    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    dimension = embeddings.shape[1]

    if faiss_index is None:
        # Create a new flat L2 index
        faiss_index = faiss.IndexFlatL2(dimension)

    faiss_index.add(embeddings)
    document_store.extend(chunks)

    print(f"Added {len(chunks)} chunks. Total chunks in store: {len(document_store)}")


# ── 4. Retrieve Relevant Chunks ───────────────────────────────────────────────
def retrieve_chunks(query: str, top_k: int = 4) -> list[dict]:
    """Find top_k most relevant chunks for the query using FAISS."""
    global faiss_index, document_store

    if faiss_index is None or len(document_store) == 0:
        return []

    query_embedding = embed_texts([query])
    distances, indices = faiss_index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx != -1 and idx < len(document_store):
            results.append(document_store[idx])

    return results


# ── 5. Generate Answer with Groq (RAG) ───────────────────────────────────────
def rag_answer(query: str, chat_history: list = []) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from FAISS
    2. Build prompt with context
    3. Send to Groq LLM
    4. Return answer + sources
    """
    # Step 1: Retrieve
    relevant_chunks = retrieve_chunks(query, top_k=4)
    has_context = len(relevant_chunks) > 0

    # Step 2: Build context string
    if has_context:
        context = "\n\n---\n\n".join([c["text"] for c in relevant_chunks])
        sources = list(set([c["source"] for c in relevant_chunks]))
        system_prompt = f"""You are a helpful AI assistant. Answer the user's question using the context provided below.
If the answer is found in the context, use it. If not, answer from your general knowledge and mention that.
Be concise, clear, and helpful.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}"""
    else:
        sources = []
        system_prompt = """You are a helpful AI assistant. No documents have been uploaded yet.
Answer the user's question using your general knowledge. Be concise and helpful.
If they ask about a specific document, suggest they upload it first."""

    # Step 3: Build message history for Groq
    messages = [{"role": "system", "content": system_prompt}]

    # Add last 6 messages from chat history for context
    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"] if msg["role"] != "bot" else "assistant",
            "content": msg["content"]
        })

    # Add current user question
    messages.append({"role": "user", "content": query})

    # Step 4: Call Groq
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    answer = response.choices[0].message.content

    return {
        "answer": answer,
        "sources": sources,
        "used_rag": has_context,
        "chunks_retrieved": len(relevant_chunks)
    }


# ── 6. Save / Load FAISS index ────────────────────────────────────────────────
def save_index():
    """Persist FAISS index and document store to disk."""
    if faiss_index:
        faiss.write_index(faiss_index, f"{FAISS_INDEX_PATH}.index")
        with open(f"{FAISS_INDEX_PATH}.pkl", "wb") as f:
            pickle.dump(document_store, f)


def load_index():
    """Load existing FAISS index from disk on startup."""
    global faiss_index, document_store
    try:
        if os.path.exists(f"{FAISS_INDEX_PATH}.index"):
            faiss_index = faiss.read_index(f"{FAISS_INDEX_PATH}.index")
            with open(f"{FAISS_INDEX_PATH}.pkl", "rb") as f:
                document_store = pickle.load(f)
            print(f"Loaded existing FAISS index with {len(document_store)} chunks")
    except Exception as e:
        print(f"No existing index found, starting fresh: {e}")


def clear_index():
    """Clear all documents from FAISS index."""
    global faiss_index, document_store
    faiss_index = None
    document_store = []
    print("FAISS index cleared")


def get_index_stats() -> dict:
    """Return info about current index."""
    return {
        "total_chunks": len(document_store),
        "documents": list(set([c["source"] for c in document_store])),
        "index_ready": faiss_index is not None
    }
