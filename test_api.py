"""Test the API endpoints"""
import time
import requests
import json

# Give server time to start
print("Waiting for server to start...")
time.sleep(5)

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing /health endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_vector_store_stats():
    """Test vector store stats endpoint"""
    print("\n=== Testing /vector-store/stats endpoint ===")
    try:
        response = requests.get(f"{BASE_URL}/vector-store/stats", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_query():
    """Test query endpoint"""
    print("\n=== Testing /query endpoint ===")
    try:
        payload = {
            "query": "What is artificial intelligence?",
            "top_k": 3,
            "use_agent": False
        }
        response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("AI Agent RAG System - API Test Suite")
    print("=" * 60)
    
    results = {
        "Health": test_health(),
        "Vector Store Stats": test_vector_store_stats(),
        "Query": test_query()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
