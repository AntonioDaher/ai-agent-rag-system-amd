#!/usr/bin/env python3
"""Simple script to start the server"""
import subprocess
import sys
import time

# Start the server
print("Starting AI Agent RAG System...")
subprocess.run([
    sys.executable, "-m", "uvicorn", 
    "src.api.server_lite:app",
    "--host", "127.0.0.1",
    "--port", "9011"
], cwd=r"c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system")
