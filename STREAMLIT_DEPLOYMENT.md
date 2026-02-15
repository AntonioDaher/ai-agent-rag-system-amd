# Streamlit Deployment Guide

This project has two parts:
1) FastAPI server (the RAG backend)
2) Streamlit UI (the public web app)

For public sharing, host the FastAPI server separately, then point Streamlit to it.

## Recommended public setup

- FastAPI server: Render or Railway (simple, reliable, HTTPS)
- Streamlit UI: Streamlit Community Cloud

This split keeps your API keys safe and provides stable endpoints.

## 1) Deploy FastAPI (server_lite)

Option A: Render (recommended)
1. Create a new Web Service.
2. Set the repo and branch.
3. Build command:
   pip install -r requirements.txt
4. Start command:
   python -m src.api.server_lite
5. Add environment variables:
   GROQ_API_KEY=your_key_here
   RAG_API_KEY=your_api_key_here
   RAG_RATE_LIMIT_PER_MIN=60
   RAG_ALLOWED_IPS=1.2.3.4,5.6.7.8
   RAG_API_URL=https://your-render-url

Option B: Railway
1. Create a new project and add your repo.
2. Use the same build and start commands as above.
3. Add environment variables as above.

Note: The server will expose /docs and /query endpoints.

## 2) Deploy Streamlit UI

Option A: Streamlit Community Cloud
1. Create a new app from your repo.
2. Entry point: streamlit_app.py
3. Add secrets (optional):
   RAG_API_URL=https://your-api-domain
   RAG_API_KEY=your_api_key_here
   RAG_RATE_LIMIT_PER_MIN=60
   RAG_ALLOWED_IPS=

Option B: Any VM or container
1. Install requirements.
2. Run:
   streamlit run streamlit_app.py
3. Set environment:
   RAG_API_URL=https://your-api-domain
   RAG_API_KEY=

## 3) Security notes

- Keep GROQ_API_KEY on the FastAPI server only.
- If you enable RAG_API_KEY, keep it on the Streamlit side only.
- Use HTTPS for the public API URL.
- Consider setting RAG_RATE_LIMIT_PER_MIN and RAG_ALLOWED_IPS for public safety.
- Consider adding auth on the FastAPI server if exposing publicly.

## 4) Local testing

1. Start the API:
   python -m src.api.server_lite
2. Start Streamlit:
   streamlit run streamlit_app.py
3. Open:
   http://localhost:8501
