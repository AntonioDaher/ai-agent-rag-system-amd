# AI Agent RAG System - Quick Start Guide

<!-- Optional badges (replace placeholders) -->
<!--
[![Render](https://img.shields.io/badge/Deploy-Render-blue?logo=render)](https://render.com)
[![Streamlit](https://img.shields.io/badge/Open-Streamlit-orange?logo=streamlit)](https://streamlit.io)
-->

## Overview
A production-ready Generative AI application enabling enterprise users to query documents using autonomous AI agents with Retrieval-Augmented Generation (RAG).

## Key Features
- 📄 Multi-format document support (PDF, TXT, CSV, Excel, DOCX)
- 🔍 Semantic search using FAISS vector database
- 🤖 Autonomous AI agents for intelligent reasoning
- 🛡️ Safety controls preventing hallucinations
- ⚡ FastAPI REST API for easy integration
- 📊 Comprehensive query response with source tracking

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy example config
copy .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 3. Start Server
```bash
python -m src.api.server
```

Visit: http://localhost:8000/docs for interactive API documentation

### 4. Run Tests
```bash
python tests/test_all.py
```

## Streamlit UI

### 1. Start API server (recommended for public use)
```bash
python -m src.api.server_lite
```

### 1a. (Optional) Protect the API with a key
```bash
set RAG_API_KEY=your_api_key_here
```

### 2. Run Streamlit
```bash
streamlit run streamlit_app.py
```

### 3. Configure API endpoint (optional)
```bash
set RAG_API_URL=http://127.0.0.1:9011
set RAG_API_KEY=
```

### Streamlit Cloud secrets
Create `.streamlit/secrets.toml` (or use the template in `.streamlit/secrets.toml.example`):
```toml
RAG_API_URL = "https://your-api-domain"
RAG_API_KEY = "your_api_key_here"
```

## Usage Examples

### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

### Process Document
```bash
curl -X POST "http://localhost:8000/process-document" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "path/to/document.pdf"}'
```

### Query Documents
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "top_k": 5,
    "use_agent": true
  }'
```

## Project Structure
```
ai_agent_rag_system/
├── src/          # Source code
├── data/         # Documents and vector store
├── tests/        # Test suite
├── requirements.txt
├── .env.example
├── DOCUMENTATION.md
└── README.md
```

## Documentation
- **DOCUMENTATION.md** - Complete system architecture, all 10 steps, and implementation details
- **API Documentation** - http://localhost:8000/docs (when server running)

## Deployment Guide
See **STREAMLIT_DEPLOYMENT.md** for public hosting steps.

## Support
For issues or questions, refer to the DOCUMENTATION.md file's troubleshooting section.
