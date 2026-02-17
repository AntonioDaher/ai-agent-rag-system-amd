# ⚡ Quick Deploy to Streamlit Cloud

## Step 1: Go to Streamlit Cloud
Visit: https://share.streamlit.io

## Step 2: Create New App
Click **"New app"** button

## Step 3: Configure App
- **Repository**: `AntonioDaher/ai-agent-rag-system-amd`
- **Branch**: `main`
- **Main file path**: `streamlit_standalone.py`

## Step 4: Advanced Settings
Click **"Advanced settings"** before deploying:
- **Python version**: `3.11`

## Step 5: Deploy
Click **"Deploy"** button and wait 2-5 minutes

## Step 6: Add API Key
Once deployed:
1. Click **⚙️ Settings** → **Secrets**
2. Add:
   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```
3. Click **Save**

## Step 7: Get API Key
If you don't have a Groq API key:
1. Visit: https://console.groq.com
2. Sign up (free)
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key

## ✅ Done!
Your app is now live at: `https://your-app-name.streamlit.app`

---

**Need help?** See full guide: [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md)
