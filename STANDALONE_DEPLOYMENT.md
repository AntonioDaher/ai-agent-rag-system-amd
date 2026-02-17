# 🚀 Standalone Streamlit Deployment Guide

This guide shows you how to deploy your AI Agent RAG System as a standalone Streamlit app.

## ✨ What's Different?

**Standalone Version** (Recommended):
- ✅ Single app deployment
- ✅ All AI functionality built-in
- ✅ No separate API server needed
- ✅ Simpler configuration
- ✅ One free tier service instead of two

**Split Version** (Not recommended for beginners):
- ⚠️ Requires two separate deployments
- ⚠️ API backend on Render + Frontend on Streamlit Cloud
- ⚠️ Complex configuration
- ⚠️ Multiple points of failure

## 📋 Prerequisites

1. **Groq API Key** (Free)
   - Sign up at: https://console.groq.com
   - Create API key in dashboard
   - Free tier: 30 requests/minute

2. **Streamlit Cloud Account** (Free)
   - Sign up at: https://streamlit.io/cloud
   - Connect your GitHub account

## 🎯 Deployment Steps

### Step 1: Push to GitHub

Make sure your code is on GitHub:

```bash
cd "c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system"
git add .
git commit -m "Add standalone Streamlit app"
git push
```

### Step 2: Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository: `AntonioDaher/ai-agent-rag-system-amd`
4. Set main file path: `streamlit_standalone.py`
5. Click "Advanced settings"
6. Set Python version: `3.11`
7. Click "Deploy"

### Step 3: Configure Secrets

After deployment, add your API key:

1. In your Streamlit Cloud dashboard, click on your app
2. Click "⚙️ Settings" (gear icon)
3. Select "Secrets" from the sidebar
4. Add the following:

```toml
GROQ_API_KEY = "your-actual-groq-api-key-here"
```

5. Click "Save"
6. Your app will automatically restart

### Step 4: Test Your App

1. Wait for the app to build (usually 2-5 minutes)
2. Once deployed, you'll get a URL like: `https://your-app.streamlit.app`
3. The app will automatically use your API key from secrets
4. Upload a document and test a query

## 🧪 Local Testing

Test locally before deploying:

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_standalone.py
```

The app will open at `http://localhost:8501`

## 📁 File Structure

```
ai_agent_rag_system/
├── streamlit_standalone.py     # 👈 Main app file (use this!)
├── requirements.txt            # All dependencies
├── .python-version            # Forces Python 3.11
├── .streamlit/
│   ├── config.toml           # UI theme settings
│   └── secrets.toml          # Local secrets (gitignored)
├── src/                       # RAG components
│   ├── rag/
│   ├── agents/
│   ├── document_processor/
│   ├── embeddings/
│   └── retrieval/
└── data/
    └── vector_store/          # Document index (auto-created)
```

## ⚙️ Configuration Options

### In App (Sidebar):
- **Groq API Key**: Your API key
- **LLM Model**: Choose from 3 models
- **Temperature**: Control randomness (0.0 - 1.0)

### In Code (`src/config/settings.py`):
- **Chunk Size**: 500 tokens (default)
- **Chunk Overlap**: 50 tokens (default)  
- **Embedding Model**: `intfloat/multilingual-e5-small`

## 🔧 Troubleshooting

### Build Fails on Streamlit Cloud

**Problem**: "tiktoken requires Rust compiler"
**Solution**: Ensure `.python-version` contains `3.11` (not 3.12 or 3.13)

**Problem**: "numpy version incompatibility"
**Solution**: Add to `requirements.txt`:
```
numpy>=1.24.3,<2.0
```

### App Loads But Shows Error

**Problem**: "Failed to initialize pipeline"
**Solution**: Check your Groq API key in Streamlit Cloud secrets

**Problem**: "No module named 'src'"
**Solution**: File must be in project root (`streamlit_standalone.py`)

### Slow Performance

**Problem**: First query is very slow
**Solution**: This is normal - models download on first use (~100MB)
- Subsequent queries are fast
- Models are cached by Streamlit

**Problem**: Upload fails for large PDFs
**Solution**: Streamlit Cloud has 200MB app memory limit
- Keep PDFs under 10MB
- Or upgrade to Streamlit Cloud paid tier

## 🎨 Customization

### Change UI Theme

Edit `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4CAF50"      # Main accent color
backgroundColor = "#FFFFFF"    # Background
secondaryBackgroundColor = "#F0F2F6"  # Sidebar
textColor = "#262730"         # Text
```

### Change Models

In the sidebar's "Advanced Settings", you can choose:
- `llama-3.3-70b-versatile` (Recommended - Newest and fastest)
- `llama3-70b-8192` (Good quality)
- `mixtral-8x7b-32768` (Good for long context)

All models are free on Groq!

### Add More File Types

Edit `src/config/settings.py`:

```python
allowed_extensions: str = "pdf,txt,csv,xlsx,docx,md,json"
```

Then implement processors in `src/document_processor/processor.py`

## 💡 Tips

1. **Use dedicated uploads folder**: Documents are processed in memory, not saved permanently
2. **Vector store persists**: The indexed documents are saved to `data/vector_store/`
3. **Reset when needed**: Use "Reset Store" button to clear all indexed documents
4. **Monitor usage**: Check Groq dashboard for API usage (30 req/min free limit)
5. **Test locally first**: Always test on local machine before deploying

## 🆘 Getting Help

- **Streamlit Docs**: https://docs.streamlit.io
- **Groq Docs**: https://console.groq.com/docs
- **Langchain Docs**: https://python.langchain.com

## 🎉 Success!

Once deployed, share your app URL with others:
- No authentication required (add if needed)
- Works on mobile devices
- Free hosting on Streamlit Cloud
- Auto-wakes from sleep on first visit

Your AI-powered document Q&A system is now live! 🚀
