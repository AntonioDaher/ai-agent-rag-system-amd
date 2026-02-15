"""Test multilingual retrieval"""
import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:9011"

pdf_path = Path("uploads/BASICS OF AI PROGRAM (IMP).pdf")

print("=" * 80)
print("MULTILINGUAL RAG SYSTEM TEST")
print("=" * 80)

# Step 1: Upload PDF
if pdf_path.exists():
    print("\n1. UPLOADING PDF WITH MULTILINGUAL EMBEDDINGS...")
    print("-" * 80)
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/upload", files=files)
    
    result = response.json()
    print(f"Status: {result.get('status')}")
    print(f"Chunks created: {result.get('chunks_created')}")
    print()
    
    # Step 2: Test English query
    print("2. TESTING ENGLISH QUERY...")
    print("-" * 80)
    query_en = "What is the name of the institute?"
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": query_en, "top_k": 3}
    )
    
    result = response.json()
    print(f"Query: {query_en}")
    print(f"Response: {result.get('response')[:200]}...")
    print(f"Retrieved {result.get('doc_count')} documents")
    print()
    
    # Step 3: Test Arabic query
    print("3. TESTING ARABIC QUERY (cross-lingual)...")
    print("-" * 80)
    query_ar = "ما هو اسم المعهد؟"
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": query_ar, "top_k": 3}
    )
    
    result = response.json()
    print(f"Query: {query_ar}")
    print(f"Response: {result.get('response')[:200]}...")
    print(f"Retrieved {result.get('doc_count')} documents")
    print()
    
    # Step 4: Test specific keyword query
    print("4. TESTING SPECIFIC KEYWORD QUERY...")
    print("-" * 80)
    query_keyword = "IMP institute management"
    
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": query_keyword, "top_k": 3}
    )
    
    result = response.json()
    print(f"Query: {query_keyword}")
    print(f"Response: {result.get('response')[:300]}...")
    print(f"Retrieved {result.get('doc_count')} documents")
    
    print("\n" + "=" * 80)
    print("✓ MULTILINGUAL RETRIEVAL TEST COMPLETE")
    print("=" * 80)
    
else:
    print(f"PDF not found at {pdf_path}")
