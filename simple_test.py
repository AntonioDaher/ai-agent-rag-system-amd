"""Simple API test script - run while server is running"""
import time
import sys

def test_server():
    try:
        import requests
        print("Testing AI Agent RAG System API...\n")
        
        # Give server time to start if just launching
        print("Waiting for server to be ready...")
        time.sleep(3)
        
        base_url = "http://127.0.0.1:8000"
        
        # Test 1: Health Check
        print("\n1. Testing /health endpoint...")
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✓ PASS - Server is healthy")
                print(f"   Response: {response.json()}")
            else:
                print(f"   ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ FAIL - {str(e)}")
            return False
        
        # Test 2: Vector Store Stats
        print("\n2. Testing /vector-store/stats endpoint...")
        try:
            response = requests.get(f"{base_url}/vector-store/stats", timeout=5)
            if response.status_code == 200:
                print(f"   ✓ PASS - Vector store accessible")
                stats = response.json()
                print(f"   Total chunks: {stats.get('total_chunks', 0)}")
                print(f"   Unique documents: {stats.get('unique_documents', 0)}")
            else:
                print(f"   ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ FAIL - {str(e)}")
        
        # Test 3: Query (simple, without agent)
        print("\n3. Testing /query endpoint...")
        try:
            payload = {
                "query": "What is machine learning?",
                "top_k": 2,
                "use_agent": False
            }
            response = requests.post(f"{base_url}/query", json=payload, timeout=15)
            if response.status_code == 200:
                print(f"   ✓ PASS - Query processed")
                result = response.json()
                print(f"   Query: {result.get('query')}")
                print(f"   Response: {result.get('response')[:100]}...")
                print(f"   Documents retrieved: {len(result.get('retrieved_docs', []))}")
            else:
                print(f"   ✗ FAIL - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ FAIL - {str(e)}")
        
        print("\n" + "="*60)
        print("API Testing Complete!")
        print("="*60)
        print("\nTo access full API documentation:")
        print("  → Open http://127.0.0.1:8000/docs in your browser")
        print("\nTo test more endpoints:")
        print("  → Use the Swagger UI at /docs")
        
        return True
        
    except ImportError:
        print("Error: requests library not installed")
        print("Install with: pip install requests")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
