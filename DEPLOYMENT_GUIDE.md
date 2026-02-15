# 🚀 Complete Deployment Guide

## Overview
Deploy your AI Agent RAG System to make it publicly accessible:
- **Backend API**: Render.com (free tier)
- **Frontend UI**: Streamlit Cloud (free tier)

---

## 📋 Step 1: Push to GitHub

### 1.1 Commit Your Code
```powershell
cd "C:/Users/HP SPECTRE/Downloads/Edureka (Final Project)/ai_agent_rag_system"
git add .
git commit -m "Initial commit - AI Agent RAG System"
```

### 1.2 Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `ai-agent-rag-system` (or your preferred name)
3. Keep it **Public** (required for free deployments)
4. **Don't** initialize with README (you already have one)
5. Click "Create repository"

### 1.3 Push to GitHub
```powershell
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/ai-agent-rag-system.git
git branch -M main
git push -u origin main
```

---

## 🔧 Step 2: Deploy Backend to Render

### 2.1 Sign Up for Render
1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `ai-agent-rag-system`
3. Configure the service:
   - **Name**: `ai-agent-rag-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m src.api.server_lite`
   - **Plan**: `Free`

### 2.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**:

| Key | Value | Notes |
|-----|-------|-------|
| `GROQ_API_KEY` | `your_groq_api_key_here` | **Required** - Get from https://console.groq.com |
| `RAG_API_KEY` | `your_secure_api_key` | **Optional** - For API authentication |
| `RAG_RATE_LIMIT_PER_MIN` | `60` | Optional - Rate limiting |
| `RAG_ALLOWED_IPS` | `` | Optional - Leave empty for public access |

### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. **Copy your URL**: `https://ai-agent-rag-api-xxxx.onrender.com`
4. Test it: `https://your-url/health`

---

## 🎨 Step 3: Deploy Frontend to Streamlit Cloud

### 3.1 Sign Up for Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### 3.2 Create New App
1. Click **"New app"**
2. Select your repository: `YOUR_USERNAME/ai-agent-rag-system`
3. Configure:
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom name (e.g., `your-app-name`)

### 3.3 Add Secrets
Click **"Advanced settings"** → **"Secrets"**

Add this configuration (replace with your values):
```toml
RAG_API_URL = "https://ai-agent-rag-api-xxxx.onrender.com"
RAG_API_KEY = "your_secure_api_key"
```

**Important**: Use the Render URL you copied in Step 2.4!

### 3.4 Deploy
1. Click **"Deploy!"**
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## ✅ Step 4: Test Your Deployment

### 4.1 Test Backend API
```powershell
# Replace with your Render URL
Invoke-RestMethod -Uri 'https://ai-agent-rag-api-xxxx.onrender.com/health' | ConvertTo-Json
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-15T...",
  "version": "1.0.0",
  "message": "AI Agent RAG System is operational"
}
```

### 4.2 Test Frontend UI
1. Open your Streamlit app URL: `https://your-app-name.streamlit.app`
2. Test both query modes:
   - **LLM Direct Query**: Ask any question
   - **RAG Query**: Upload a document and query it

---

## 🔐 Security Checklist

- [ ] **Never commit `.env` file** (already in `.gitignore`)
- [ ] Set `RAG_API_KEY` for API authentication
- [ ] Configure `RAG_RATE_LIMIT_PER_MIN` to prevent abuse
- [ ] Monitor Render logs for unusual activity
- [ ] Keep `GROQ_API_KEY` private (only on Render backend)
- [ ] Use HTTPS URLs (Render provides this automatically)

---

## 📊 Free Tier Limits

### Render.com Free Tier:
- ✅ 512MB RAM
- ✅ HTTPS included
- ⚠️ Sleeps after 15 min of inactivity (30-60s cold start)
- ⚠️ 750 hours/month (sufficient for demos)

### Streamlit Cloud Free Tier:
- ✅ 1GB RAM
- ✅ Unlimited viewers
- ✅ Always-on (no sleep)
- ⚠️ Public repository required

---

## 🔄 Updating Your Deployment

### Update Backend:
```powershell
git add .
git commit -m "Update backend"
git push origin main
```
Render will auto-deploy in ~5 minutes.

### Update Frontend:
```powershell
git add .
git commit -m "Update frontend"
git push origin main
```
Streamlit will auto-redeploy in ~2 minutes.

---

## 🐛 Troubleshooting

### Backend Issues:
1. **Check Render logs**: Dashboard → Logs tab
2. **Verify environment variables**: Settings → Environment
3. **Test health endpoint**: `https://your-url/health`
4. **Check build logs**: Look for Python errors

### Frontend Issues:
1. **Check Streamlit logs**: App → Manage app → Logs
2. **Verify secrets**: Settings → Secrets
3. **Ensure RAG_API_URL is correct** (with https://)
4. **Test backend first** before debugging frontend

### Common Errors:
- **504 Gateway Timeout**: Backend is sleeping (wait 60s on free tier)
- **Connection refused**: Wrong `RAG_API_URL` in Streamlit secrets
- **401 Unauthorized**: API key mismatch between frontend/backend
- **Build failed**: Check `requirements.txt` for missing packages

---

## 💡 Next Steps

1. **Custom Domain** (optional):
   - Render: Settings → Custom Domain
   - Streamlit: Settings → Custom Domain (requires paid plan)

2. **Monitoring**:
   - Set up Render email alerts
   - Monitor Groq API usage at https://console.groq.com

3. **Share Your App**:
   - Share the Streamlit URL: `https://your-app-name.streamlit.app`
   - Users can access it without any setup!

---

## 📞 Support

- Render: https://render.com/docs
- Streamlit: https://docs.streamlit.io/deploy
- Groq API: https://console.groq.com/docs

