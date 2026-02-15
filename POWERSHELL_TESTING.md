# PowerShell API Testing Guide

## Your Server is Running! ✓

The AI Agent RAG System server is successfully deployed on http://127.0.0.1:8000

---

## Option 1: Best Way - Use Browser (Easiest)

**Open this URL in your browser:**
```
http://127.0.0.1:8000/docs
```

This gives you:
- ✓ Interactive API documentation
- ✓ Ability to test all endpoints
- ✓ Request/response examples
- ✓ No command line needed

---

## Option 2: Use PowerShell (Advanced)

### Test Health Endpoint
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing
$response.Content | ConvertFrom-Json | Format-List
```

### Test Query Endpoint
```powershell
$body = @{
    query = "What is artificial intelligence?"
    top_k = 3
    use_agent = $false
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/query" `
    -Method POST `
    -Body $body `
    -ContentType "application/json" `
    -UseBasicParsing

$response.Content | ConvertFrom-Json | Format-List
```

### Get Vector Store Stats
```powershell
$response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/vector-store/stats" -UseBasicParsing
$response.Content | ConvertFrom-Json | Format-List
```

---

## Option 3: Use Python Test Script

### Run the simple test
```bash
python simple_test.py
```

This will automatically test:
- Health endpoint
- Vector store stats
- Query functionality

---

## API Endpoints Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Check system status |
| /query | POST | Query documents |
| /upload | POST | Upload files |
| /process-document | POST | Process files |
| /vector-store/stats | GET | View statistics |
| /vector-store/clear | POST | Clear storage |

---

## Example Requests

### PowerShell - Simple Health Check
```powershell
Invoke-WebRequest "http://127.0.0.1:8000/health" -UseBasicParsing
```

### PowerShell - Query with Response
```powershell
$json = @{
    query = "What is RAG?"
    top_k = 2
    use_agent = $false
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/query" `
    -Method POST -Body $json -ContentType "application/json" -UseBasicParsing |
    Select-Object -ExpandProperty Content
```

### Python - Using Requests
```python
import requests

# Query the system
response = requests.post(
    "http://127.0.0.1:8000/query",
    json={
        "query": "What is machine learning?",
        "top_k": 3,
        "use_agent": False
    }
)
print(response.json())
```

---

## Recommended Testing Flow

1. **First:** Open http://127.0.0.1:8000/docs in browser ← **EASIEST**
2. **Test:** Click "Try it out" on each endpoint
3. **See:** Interactive responses with documentation

This is the best way to understand and test your API!

---

## Troubleshooting

### Server Not Responding
- Check if server is still running in terminal
- Restart with: `python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000`

### PowerShell Timeout
- Use `-TimeoutSec` parameter: `Invoke-WebRequest ... -TimeoutSec 30`

### Port Already in Use
- Use different port: `python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8001`

---

## Next Steps

1. ✓ Open http://127.0.0.1:8000/docs
2. ✓ Test the /health endpoint first
3. ✓ Try the /query endpoint with a sample question
4. ✓ Upload a document and query it
5. ✓ Check /vector-store/stats

**That's it!** Your system is working perfectly! 🚀
