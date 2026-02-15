"""Minimal API server for testing"""
import os
import sys
from pathlib import Path

os.environ['OPENBLAS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import FastAPI
from datetime import datetime

# Create app
app = FastAPI(
    title="AI Agent RAG System",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Agent RAG System API", "docs": "/docs"}
