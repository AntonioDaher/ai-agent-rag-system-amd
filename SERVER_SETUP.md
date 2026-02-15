# Server Configuration & Startup Guide

## Server Versions Available

Your AI Agent RAG System has **two server versions** optimized for different scenarios:

### ✅ Recommended: Lightweight Server (server_lite.py)
- **Status:** Stable and working
- **Best for:** Quick testing, demos, development
- **Startup:** `start_server.bat` (updated to use this)
- **Features:** API endpoints, core functionality
- **Performance:** Instant startup, no model loading delays
- **Command:** `python -m uvicorn src.api.server_lite:app --host 127.0.0.1 --port 8000`

### 🔧 Full-Featured Server (server.py)
- **Status:** Full AI capabilities
- **Best for:** Production use with all features
- **Features:** Complete LLM, embeddings, agents, safety controls
- **Startup:** Slower (loads embedding models)
- **Command:** `python run_server.py`

---

## Quick Start

### Option 1: Double-Click (Easiest)
```
double-click: start_server.bat
```
This now uses the stable lightweight server.

### Option 2: Command Line
```bash
cd "c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system"
python -m uvicorn src.api.server_lite:app --host 127.0.0.1 --port 8000
```

### Result
```
✓ Server running at http://127.0.0.1:8000
✓ API docs at http://127.0.0.1:8000/docs
✓ Ready to use!
```

---

## Switching Between Versions

### To Use Lightweight Server (Recommended for Now)
```bash
python -m uvicorn src.api.server_lite:app --host 127.0.0.1 --port 8000
```

### To Use Full-Featured Server
```bash
# First time may take 30-60 seconds to load models
python run_server.py

# Or directly:
python -m uvicorn src.api.server:app --host 127.0.0.1 --port 8000
```

---

## What's Updated

✅ **start_server.bat** - Now uses server_lite.py (stable version)
✅ **server_lite.py** - Enhanced with query endpoint support
✅ **run_server.py** - Still available for full-featured version

---

## Why Two Versions?

**Lightweight Version (server_lite.py):**
- Avoids Fortran library issues on Windows
- Starts instantly
- Good for testing API endpoints
- Can load full features on-demand

**Full-Featured Version (server.py):**
- All 10 output steps fully implemented
- Complete LLM integration
- All safety controls active
- Autonomous agents operational

---

## Testing the Server

### In Browser
1. Open: http://127.0.0.1:8000/docs
2. Click "Try it out" on any endpoint
3. See live responses

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Query Endpoint
```bash
# PowerShell
$body = @{query="What is AI?"; top_k=3; use_agent=$false} | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/query" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

---

## Available Endpoints

Both servers provide these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | System health check |
| / | GET | Root endpoint info |
| /query | POST | Query documents |
| /vector-store/stats | GET | Vector store statistics |

Full-featured server also includes:
| /upload | POST | Upload documents |
| /process-document | POST | Process files |
| /vector-store/clear | POST | Clear storage |

---

## Troubleshooting

### Server won't start
- Make sure port 8000 is not in use
- Try different port: `--port 8001`
- Check Python version (3.11+ required)

### Can't connect to http://127.0.0.1:8000
- Verify server output shows "Uvicorn running on"
- Try http://localhost:8000 instead
- Check firewall settings

### Slow startup
- Lightweight version (lite) should be instant
- Full version takes 30-60 seconds (normal)

---

## Recommended Workflow

1. **Start with:** `start_server.bat` (lightweight version)
2. **Test endpoints:** Open http://127.0.0.1:8000/docs
3. **When ready:** Switch to full version with `python run_server.py`

---

## Files Involved

```
ai_agent_rag_system/
├── src/api/
│   ├── server.py          (Full-featured version)
│   ├── server_lite.py     (Lightweight version - RECOMMENDED)
│   └── models.py          (Request/response schemas)
├── start_server.bat       (UPDATED - uses server_lite)
├── run_server.py          (Full-featured launcher)
└── POWERSHELL_TESTING.md  (Testing guide)
```

---

## Next Steps

✓ Run: `start_server.bat`
✓ Open: http://127.0.0.1:8000/docs
✓ Test: Try the /health endpoint
✓ Query: Test the /query endpoint
✓ Explore: Check all available endpoints

**Your system is ready!** 🚀
