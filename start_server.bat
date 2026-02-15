@echo off
REM Start the AI Agent RAG System Server
REM This script uses the stable lightweight server version

REM Set environment variables for stability
set OPENBLAS=1
set OMP_NUM_THREADS=1
set MKL_THREADING_LAYER=GNU

REM Navigate to project directory
cd /d "c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system"

REM Start the server (using stable lite version)
echo Starting AI Agent RAG System Server...
echo Server will be available at: http://127.0.0.1:8000
echo Swagger UI: http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.api.server_lite:app --host 127.0.0.1 --port 8000

pause
