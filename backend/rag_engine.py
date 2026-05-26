import os
import faiss
import numpy as np
import pickle
from groq import Groq
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

print("Loading embedding model... (first time may take a minute)")
embedding_model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "faiss_index")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# In-memory storage
document_store = []
faiss_index = None


# ── 1. Text Splitting ─────────────────────────────────────────────────────────
def split_text(text: str, source: str) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_text(text)
    return [{"text": chunk, "source": source} for chunk in chunks]


# ── 2. Embedding ──────────────────────────────────────────────────────────────
def embed_texts(texts: list[str]) -> np.ndarray:
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    return embeddings.astype("float32")


# ── 3. Add Document to FAISS ──────────────────────────────────────────────────
def add_to_faiss(chunks: list[dict]):
    global faiss_index, document_store
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    dimension = embeddings.shape[1]
    if faiss_index is None:
        faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)
    document_store.extend(chunks)
    print(f"Added {len(chunks)} chunks. Total chunks in store: {len(document_store)}")


# ── 4. Retrieve Relevant Chunks with Threshold ────────────────────────────────
def retrieve_chunks(query: str, top_k: int = 4) -> list[dict]:
    """
    Find relevant chunks using FAISS with a similarity threshold.
    FAISS L2 distance: lower = more similar.
    Threshold 1.2 filters out chunks not relevant to the query.
    """
    global faiss_index, document_store

    if faiss_index is None or len(document_store) == 0:
        return []

    query_embedding = embed_texts([query])
    distances, indices = faiss_index.search(query_embedding, top_k)

    SIMILARITY_THRESHOLD = 2.0  # Only include chunks with distance < this

    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx != -1 and idx < len(document_store):
            if distance < SIMILARITY_THRESHOLD:
                results.append(document_store[idx])

    return results


# ── 5. RAG Answer ─────────────────────────────────────────────────────────────
def rag_answer(query: str, chat_history: list = []) -> dict:
    """
    Smart RAG pipeline:
    - If question matches document → answer from document (RAG mode)
    - If question is general → answer from Groq general knowledge
    """
    # Step 1: Retrieve relevant chunks
    relevant_chunks = retrieve_chunks(query, top_k=4)
    has_context = len(relevant_chunks) > 0

    # Step 2: Build system prompt based on context availability
    if has_context:
        context = "\n\n---\n\n".join([c["text"] for c in relevant_chunks])
        sources = list(set([c["source"] for c in relevant_chunks]))
        system_prompt = f"""You are a helpful AI assistant with two capabilities:
1. Answer questions from uploaded documents using the context below
2. Answer any general questions using your own knowledge

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

INSTRUCTIONS:
- If the user's question is clearly answered by the context above, use it and answer precisely.
- If the user's question is NOT related to the context at all (e.g. general knowledge, science, coding, math, current events), IGNORE the context and answer from your general knowledge.
- You are a full AI assistant — never refuse to answer general questions.
- Be helpful, clear, and concise."""
    else:
        sources = []
        system_prompt = """You are a helpful and intelligent AI assistant powered by Groq (Llama 3).
Answer any question the user asks using your general knowledge.
Be concise, accurate, and friendly.
If asked about a specific file or document, suggest they upload it using the upload panel on the left."""

    # Step 3: Build messages with history
    messages = [{"role": "system", "content": system_prompt}]

    for msg in chat_history[-6:]:
        messages.append({
            "role": msg["role"] if msg["role"] != "bot" else "assistant",
            "content": msg["content"]
        })

    messages.append({"role": "user", "content": query})

    # Step 4: Call Groq LLM
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.7,
    )

    answer = response.choices[0].message.content

    # Step 5: If context was available but Groq answered from general knowledge,
    # don't show the document as source
    return {
        "answer": answer,
        "sources": sources if has_context else [],
        "used_rag": has_context,
        "chunks_retrieved": len(relevant_chunks)
    }


# ── 6. Save / Load / Clear ────────────────────────────────────────────────────
def save_index():
    if faiss_index:
        faiss.write_index(faiss_index, f"{FAISS_INDEX_PATH}.index")
        with open(f"{FAISS_INDEX_PATH}.pkl", "wb") as f:
            pickle.dump(document_store, f)


def load_index():
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
    global faiss_index, document_store
    faiss_index = None
    document_store = []
    print("FAISS index cleared")


def get_index_stats() -> dict:
    return {
        "total_chunks": len(document_store),
        "documents": list(set([c["source"] for c in document_store])),
        "index_ready": faiss_index is not None
    }
