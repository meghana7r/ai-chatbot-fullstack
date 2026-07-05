"""
DEMO SCRIPT: Show RAG internals for team presentation
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(step_num, text):
    print(f"\n📌 STEP {step_num}: {text}")
    print("-" * 70)

def demo_rag_process():
    session_id = "demo_presentation"
    
    print_header("🎯 RAG SYSTEM DEMONSTRATION")
    print("This demo shows how our RAG (Retrieval Augmented Generation) works")
    
    # STEP 1: Upload Document
    print_step(1, "Uploading Document")
    
    file_path = input("\n📁 Enter path to a PDF/TXT/DOCX file to demo: ").strip()
    
    with open(file_path, 'rb') as f:
        filename = file_path.split('/')[-1]
        response = requests.post(
            f"{BASE_URL}/chat/upload?session_id={session_id}",
            files={"file": (filename, f)}
        )
    
    upload_result = response.json()
    print(f"\n✅ Upload Response:")
    print(json.dumps(upload_result, indent=2))
    
    time.sleep(1)
    
    # STEP 2: Show Chunks
    print_step(2, "Document Chunking - How Text is Split")
    
    chunks_response = requests.get(
        f"{BASE_URL}/chat/debug/chunks/{session_id}/{filename}"
    )
    
    print(f"\n🔍 DEBUG - Status Code: {chunks_response.status_code}")
    print(f"🔍 DEBUG - Raw Response: {chunks_response.text}")
    
    chunks_data = chunks_response.json()
    
    if 'total_chunks' not in chunks_data:
        print(f"\n❌ ERROR: Endpoint returned unexpected response")
        print(f"Response was: {chunks_data}")
        return
    
    print(f"\n📊 Total Chunks Created: {chunks_data['total_chunks']}")
    print(f"📊 Embedding Model: {chunks_data['embedding_model']}")
    print(f"📊 Embedding Dimensions: {chunks_data['embedding_dimensions']}")
    
    print("\n📚 CHUNK DETAILS:")
    for chunk in chunks_data['chunks']:
        print(f"\n  Chunk #{chunk['chunk_number']}:")
        print(f"  Length: {chunk['chunk_length']} characters")
        print(f"  Text: {chunk['chunk_text'][:150]}...")
    
    time.sleep(1)
    
    # STEP 3: Search Query Demo
    print_step(3, "Query Processing - How AI Finds Relevant Chunks")
    
    query = input("\n💬 Enter a question about the document: ").strip()
    
    search_response = requests.post(
        f"{BASE_URL}/chat/debug/search-scores/{session_id}",
        params={"query": query}
    )
    
    print(f"\n🔍 DEBUG - Status Code: {search_response.status_code}")
    print(f"🔍 DEBUG - Raw Response: {search_response.text}")
    
    search_data = search_response.json()
    
    if 'results' not in search_data:
        print(f"\n❌ ERROR: Search endpoint returned unexpected response")
        return
    
    print(f"\n🔍 Query: '{search_data['query']}'")
    print(f"🔍 Searched {search_data['total_chunks_searched']} chunks")
    print(f"🔍 Relevance Threshold: {search_data['relevance_threshold']}")
    print(f"🔍 Will use RAG: {search_data['would_use_rag']}")
    
    print("\n📊 SIMILARITY SCORES (Ranked):")
    for result in search_data['results']:
        print(f"\n  Rank #{result['rank']}: Score = {result['similarity_score']}")
        print(f"  Chunk: {result['chunk_preview']}")
    
    time.sleep(1)
    
    # STEP 4: Full Answer Generation
    print_step(4, "Final Answer Generation - RAG + Groq AI")
    
    chat_response = requests.post(
        f"{BASE_URL}/chat/",
        json={
            "message": query,
            "session_id": session_id,
            "history": []
        }
    )
    chat_data = chat_response.json()
    
    print(f"\n🤖 AI Response Source: {chat_data.get('source', 'unknown')}")
    print(f"\n💡 FINAL ANSWER:")
    print(f"{chat_data.get('bot_reply', 'No reply')}")
    
    print_header("✅ DEMONSTRATION COMPLETE")


if __name__ == "__main__":
    demo_rag_process()
