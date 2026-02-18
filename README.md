# 🤖 AI Agent RAG System - Enterprise Document Q&A

**Capstone Project: Generative AI for Enterprise Document Understanding**

A complete Retrieval-Augmented Generation (RAG) system with AI agents for intelligent document question-answering. This standalone Streamlit application processes enterprise documents and provides accurate, grounded responses using LLM technology.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [System Components](#system-components)
5. [Setup & Installation](#setup--installation)
6. [Usage Guide](#usage-guide)
7. [Deployment](#deployment)
8. [Output Steps Coverage](#output-steps-coverage)
9. [Limitations & Challenges](#limitations--challenges)
10. [Technical Documentation](#technical-documentation)

---

## 🎯 Overview

This system enables enterprise users to:
- Upload documents in multiple formats (PDF, TXT, CSV, XLSX, DOCX)
- Ask natural language questions about document content
- Receive accurate, context-aware answers powered by LLMs
- Leverage AI agents for complex reasoning and multi-step queries

**Key Technology Stack:**
- **Frontend**: Streamlit (Python web framework)
- **LLM Provider**: Groq AI (free tier with high-performance models)
- **Embeddings**: Multilingual E5 (local, no API needed)
- **Vector Store**: FAISS (in-memory similarity search)
- **Framework**: LangChain (RAG orchestration)

---

## ✨ Features

### Core Capabilities
✅ **Multi-format Document Processing**
- PDF, TXT, CSV, Excel, Word documents
- Automatic format detection and text extraction
- Intelligent chunking with configurable overlap

✅ **Semantic Search**
- Vector embeddings for semantic similarity
- Context-aware document retrieval
- Multilingual support (100+ languages)

✅ **Retrieval-Augmented Generation**
- Combines document context with LLM knowledge
- Reduces hallucinations through grounding
- Citation-aware responses

✅ **AI Agent Support**
- Multi-step reasoning capabilities
- Tool-based decision making
- Complex query handling

✅ **Two Query Modes**
- **Direct LLM Query**: General knowledge Q&A
- **RAG Query**: Document-specific responses with retrieval

✅ **Safety & Reliability**
- Input validation and sanitization
- Error handling and graceful degradation
- Rate limiting support
- API key management

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│  (User Interface + Session Management + File Upload)         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG Pipeline Orchestrator                  │
└─────┬───────────┬───────────┬───────────┬──────────┬────────┘
      │           │           │           │          │
      ▼           ▼           ▼           ▼          ▼
┌──────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────────┐
│Document  │ │Chunking │ │Embedding│ │Vector  │ │LLM      │
│Processor │ │Engine   │ │Manager  │ │Store   │ │(Groq)   │
└──────────┘ └─────────┘ └─────────┘ └────────┘ └─────────┘
      │           │           │           │          │
      └───────────┴───────────┴───────────┴──────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  AI Agent     │
                    │  (Optional)   │
                    └───────────────┘
```

### Data Flow

1. **Document Upload** → User uploads files via Streamlit UI
2. **Text Extraction** → Document processor extracts text content
3. **Chunking** → Text split into overlapping chunks (500 tokens)
4. **Embedding** → Each chunk converted to vector representation
5. **Storage** → Vectors stored in FAISS index with metadata
6. **Query Processing** → User question embedded using same model
7. **Retrieval** → Top-K similar chunks retrieved via cosine similarity
8. **Generation** → LLM generates response using retrieved context
9. **Agent Enhancement** (Optional) → AI agent adds reasoning and planning

---

## 🔧 System Components

### 1. Document Processor (`src/document_processor/`)
**Purpose**: Extract text from various file formats

**Files**:
- `processor.py` - Format-specific processors (PDF, CSV, XLSX, DOCX, TXT)
- `chunker.py` - Text chunking with overlap and metadata

**Key Features**:
- Factory pattern for processor selection
- Robust error handling per format
- Preserves document metadata (filename, chunk index)

### 2. Embedding Manager (`src/embeddings/`)
**Purpose**: Convert text to vector representations

**Model**: `intfloat/multilingual-e5-small`
- 384-dimensional embeddings
- Supports 100+ languages
- Runs locally (no API costs)
- ~100MB model size

### 3. Vector Store (`src/retrieval/`)
**Purpose**: Store and retrieve document embeddings

**Technology**: FAISS (Facebook AI Similarity Search)
- In-memory index
- Cosine similarity search
- Efficient batch operations
- Persistence to disk

### 4. RAG Pipeline (`src/rag/`)
**Purpose**: Orchestrate retrieval and generation

**Workflow**:
1. Embed user query
2. Retrieve top-K relevant chunks
3. Build context-aware prompt
4. Call LLM with grounded context
5. Return response with citations

### 5. AI Agent (`src/agents/`)
**Purpose**: Handle complex multi-step queries

**Capabilities**:
- Query planning and decomposition
- Tool selection and execution
- Multi-turn reasoning
- Self-correction

### 6. Safety Guards (`src/safety/`)
**Purpose**: Ensure safe and reliable operation

**Features**:
- Input sanitization
- Output validation
- Content filtering
- Error boundaries

### 7. Configuration (`src/config/`)
**Purpose**: Centralized settings management

**Files**:
- `settings.py` - Environment-based configuration
- `logger.py` - Structured logging setup

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11 or higher
- Git
- Groq API key (free at https://console.groq.com)

### Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/AntonioDaher/ai-agent-rag-system-amd.git
cd ai-agent-rag-system-amd

# 2. Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment (optional - can use UI checkbox)
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 5. Run the application
streamlit run streamlit_standalone.py
```

The app will open at `http://localhost:8501`

---

## 📖 Usage Guide

### Basic Workflow

1. **Configure API Key**
   - Option A: Check "Use Custom API Key" and enter your key
   - Option B: Set `GROQ_API_KEY` in `.env` or secrets

2. **Select LLM Model**
   - `llama-3.3-70b-versatile` (Default - Best performance)
   - `llama-3.1-8b-instant` (Faster responses)

3. **Adjust Temperature** (0.0 - 1.0)
   - Lower (0.0-0.3): Focused, deterministic
   - Medium (0.4-0.7): Balanced
   - Higher (0.8-1.0): Creative, varied

4. **Choose Query Mode**
   - **LLM Direct Query**: General knowledge, no documents needed
   - **RAG Query**: Search uploaded documents

### RAG Query Mode

1. **Upload Documents**
   - Drag & drop or browse for files
   - Supported: PDF, TXT, CSV, XLSX, DOCX
   - Click "Upload" to process

2. **Configure Retrieval**
   - **Results (Top-K)**: Number of chunks to retrieve (1-10)
   - **Use Agent**: Enable for complex queries
   - **Show Details**: Display retrieved chunks

3. **Ask Questions**
   - Type your question in the text area
   - Click "Ask" to get answer
   - Use "Clear" to reset input

4. **Review Results**
   - Answer displayed with sources
   - Retrieved documents shown if "Show Details" enabled
   - Similarity scores for each chunk

### Direct LLM Query Mode

1. **Switch Mode**
   - Select "LLM Direct Query (No Uploads)"

2. **Ask Questions**
   - Ask any general knowledge question
   - No document upload required
   - Uses LLM's base knowledge

---

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

**Step 1: Push to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

**Step 2: Deploy to Streamlit**
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select repository: `AntonioDaher/ai-agent-rag-system-amd`
4. Main file: `streamlit_standalone.py`
5. Python version: `3.11`
6. Click "Deploy"

**Step 3: Add Secrets**
1. In Streamlit dashboard, click Settings → Secrets
2. Add:
```toml
GROQ_API_KEY = "your-groq-api-key-here"
```
3. Save and wait for restart

**Your app will be live at**: `https://your-app-name.streamlit.app`

### Troubleshooting Deployment

**Build fails with "tiktoken requires Rust"**
- Solution: Ensure `.python-version` has `3.11`

**"Failed to initialize pipeline"**
- Solution: Check Groq API key in Streamlit secrets

**Slow first query**
- Expected: Embedding model downloads (~100MB) on first use
- Subsequent queries are fast

See `STANDALONE_DEPLOYMENT.md` for detailed deployment guide.

---

## ✅ Output Steps Coverage

This project implements all 10 required output steps:

### Step 1: Project Foundation ✅
**Implemented**:
- Git repository with version control
- Environment configuration (`.env`, `.env.example`)
- Structured codebase (`src/` directory organization)
- Virtual environment setup
- Dependency management (`requirements.txt`)

**Files**: `.gitignore`, `.env.example`, `.python-version`, `requirements.txt`

---

### Step 2: User Interaction Layer ✅
**Implemented**:
- Streamlit web interface with intuitive UI
- File upload component (drag & drop)
- Text input for natural language questions
- Configuration sidebar (API key, model, temperature)
- Real-time feedback and progress indicators

**Files**: `streamlit_standalone.py` (lines 150-250)

---

### Step 3: Document Ingestion ✅
**Implemented**:
- Multi-format support: PDF, TXT, CSV, XLSX, DOCX
- Factory pattern for processor selection
- Robust error handling per format
- Batch upload support
- File validation and sanitization

**Files**: 
- `src/document_processor/processor.py`
- `streamlit_standalone.py::process_uploaded_file()`

**Supported Formats**:
```python
PDF    → PyPDF2 extraction
TXT    → Direct text read
CSV    → Pandas DataFrame to text
XLSX   → Excel sheet parsing
DOCX   → python-docx paragraph extraction
```

---

### Step 4: Data Preparation for Semantic Search ✅
**Implemented**:
- Intelligent text chunking (500 tokens, 50 overlap)
- Token-aware splitting using tiktoken
- Metadata preservation (source file, chunk index)
- Chunk deduplication
- Configurable chunk size and overlap

**Files**: 
- `src/document_processor/chunker.py`
- `src/config/settings.py` (chunk_size, chunk_overlap)

**Chunking Strategy**:
```python
chunk_size = 500      # Tokens per chunk
chunk_overlap = 50    # Token overlap between chunks
```

---

### Step 5: Vector-Based Knowledge Store ✅
**Implemented**:
- Embedding generation using E5-small (384 dims)
- FAISS vector database for similarity search
- Efficient batch embedding operations
- Persistent storage (save/load index)
- Metadata tracking for each vector

**Files**: 
- `src/embeddings/embedding.py` (EmbeddingManager)
- `src/retrieval/vector_store.py` (VectorStoreManager)

**Technology Stack**:
```
Embeddings: intfloat/multilingual-e5-small
Vector DB:  FAISS (IndexFlatIP - cosine similarity)
Storage:    NumPy arrays + JSON metadata
```

---

### Step 6: Intelligent Document Retrieval ✅
**Implemented**:
- Semantic similarity search (cosine distance)
- Top-K retrieval with configurable K (1-10)
- Similarity score ranking
- Context-aware chunk selection
- Query-document relevance scoring

**Files**: 
- `src/retrieval/vector_store.py::search()`
- `src/rag/pipeline.py::retrieve()`

**Retrieval Process**:
1. Embed query using same model
2. Compute cosine similarity with all chunks
3. Return top-K most similar
4. Include metadata and scores

---

### Step 7: RAG Pipeline ✅
**Implemented**:
- Complete RAG workflow orchestration
- Context-aware prompt engineering
- Retrieved chunks injection into LLM prompt
- Source-grounded response generation
- Hallucination reduction through grounding

**Files**: 
- `src/rag/pipeline.py` (RAGPipeline class)
- Lines: `initialize_pipeline()`, `generate_response()`

**RAG Workflow**:
```
Query → Embed → Retrieve Top-K → Build Prompt → LLM → Response
```

**Prompt Template**:
```python
Context: {retrieved_documents}
Question: {user_query}
Answer based only on the context above...
```

---

### Step 8: Agent-Based Reasoning ✅
**Implemented**:
- AI Agent with planning and reasoning
- Tool-based architecture (retrieval tool)
- Multi-step query decomposition
- Self-reflection and correction
- Complex query handling

**Files**: 
- `src/agents/agent.py` (AIAgent class)
- Integration in `streamlit_standalone.py::process_query()`

**Agent Capabilities**:
- Query analysis and planning
- Tool selection (retrieval, generation)
- Multi-turn reasoning
- Result synthesis

**Usage**:
- Enable via "🤖 Use Agent" checkbox in UI
- Automatically handles complex queries
- Falls back to simple RAG for basic queries

---

### Step 9: Reliability & Safety Controls ✅
**Implemented**:
- Input validation and sanitization
- Error handling with graceful degradation
- Content safety checks
- Rate limiting awareness
- User feedback on errors

**Files**: 
- `src/safety/guards.py` (SafetyGuards class)
- Error handling throughout `streamlit_standalone.py`
- Logger configuration in `src/config/logger.py`

**Safety Features**:
```python
✓ Input validation (file types, query length)
✓ Error boundaries (try-catch blocks)
✓ Graceful degradation (fallback responses)
✓ Logging and monitoring
✓ API key protection (password input)
✓ Session state management
✓ Vector store reset on page load (clean slate)
```

---

### Step 10: Deployment & Documentation ✅
**Implemented**:
- Complete deployment to Streamlit Cloud
- Comprehensive documentation (this README)
- Architecture explanations
- Setup and usage instructions
- Limitations and challenges documented

**Documentation Files**:
- `README.md` (This file - Main documentation)
- `STANDALONE_DEPLOYMENT.md` (Deployment guide)
- Code comments throughout source
- Docstrings in all modules

**Deployment Status**: 
✅ Ready to deploy to Streamlit Community Cloud
✅ GitHub repository: https://github.com/AntonioDaher/ai-agent-rag-system-amd

---

## ⚠️ Limitations & Challenges

### Current Limitations

1. **Memory Constraints**
   - Vector store kept in memory (not scalable to millions of docs)
   - Streamlit limited to 1GB RAM on free tier
   - **Workaround**: Process documents in batches, clear store regularly

2. **Embedding Model Size**
   - E5-small model (~100MB) downloads on first use
   - May cause slow cold-start on deployment
   - **Workaround**: Use cached models, expect 30-60s first load

3. **Context Window Limits**
   - LLMs have max token limits (8K-32K depending on model)
   - Large documents may not fit in single context
   - **Workaround**: Chunking strategy, retrieve only top-K most relevant

4. **Groq API Rate Limits**
   - Free tier: 30 requests/minute
   - May hit limits with concurrent users
   - **Workaround**: Implement client-side throttling, use persistent store

5. **Vector Store Reset**
   - Currently resets on page refresh (by design for clean testing)
   - Users must re-upload documents each session
   - **Workaround**: Can be disabled by modifying session state logic

6. **No Authentication**
   - Public apps have no user authentication
   - Anyone with URL can access
   - **Workaround**: Add Streamlit auth or deploy privately

7. **Single Language Interface**
   - UI is English-only (but supports multilingual documents)
   - **Workaround**: Streamlit supports i18n, can be added

---

### Challenges Faced During Development

#### Challenge 1: Model Deprecations
**Problem**: Groq deprecated multiple models (llama3-70b-8192, mixtral-8x7b-32768, gemma2-9b-it, llama-3.1-70b-versatile) during development

**Solution**: 
- Implemented dynamic model selection
- Limited to verified active models (llama-3.3-70b-versatile, llama-3.1-8b-instant)
- Added model validation before API calls

#### Challenge 2: Vector Store Loading Issues
**Problem**: FAISS load() method signature changed, causing errors on initialization

**Solution**: 
- Modified initialize_pipeline to not auto-load on startup
- Implemented clean-slate approach (reset on page load)
- Added proper save/load with validation

#### Challenge 3: Tiktoken Rust Dependency
**Problem**: tiktoken library requires Rust compiler, causing deployment failures

**Solution**: 
- Forced Python 3.11 in `.python-version`
- Used pre-built wheels from PyPI
- Validated on Streamlit Cloud before final deployment

#### Challenge 4: Session State Management
**Problem**: Streamlit re-runs entire script on every interaction, losing state

**Solution**: 
- Comprehensive session state tracking
- Cache resource initialization (@st.cache_resource)
- Widget key management for form resets
- Widget refresh counter for forcing recreation

#### Challenge 5: API Key Security
**Problem**: Exposing API keys in UI by default is insecure

**Solution**: 
- Added custom API key checkbox (hidden by default)
- Use Streamlit secrets for deployment
- Password-type input field
- Clear separation of default and custom keys

#### Challenge 6: Large PDF Processing
**Problem**: Large PDFs (>50 pages) caused memory issues and timeouts

**Solution**: 
- Implemented streaming processing
- Chunk-by-chunk embedding generation
- Progress indicators for user feedback
- Backend timeout handling

---

## 📚 Technical Documentation

### Key Configuration

**Environment Variables**:
```bash
GROQ_API_KEY=your-api-key-here
CHUNK_SIZE=500
CHUNK_OVERLAP=50
EMBEDDING_MODEL=intfloat/multilingual-e5-small
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.7
```

**File Structure**:
```
ai_agent_rag_system/
├── streamlit_standalone.py         # Main application
├── requirements.txt                # Python dependencies
├── .python-version                 # Python 3.11
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── STANDALONE_DEPLOYMENT.md        # Deployment guide
├── .streamlit/
│   ├── config.toml                # UI theme settings
│   └── secrets.toml.example       # Secrets template
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent.py               # AI Agent implementation
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # Configuration management
│   │   └── logger.py              # Logging setup
│   ├── document_processor/
│   │   ├── __init__.py
│   │   ├── processor.py           # Document format handlers
│   │   └── chunker.py             # Text chunking logic
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding.py           # Embedding generation
│   ├── rag/
│   │   ├── __init__.py
│   │   └── pipeline.py            # RAG orchestration
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── vector_store.py        # FAISS vector store
│   └── safety/
│       ├── __init__.py
│       └── guards.py              # Safety validation
├── data/
│   └── vector_store/              # Persisted embeddings
│       ├── embeddings.npy
│       ├── faiss.index
│       └── metadata.json
└── uploads/                        # Temporary upload directory
```

### Dependencies

**Core Libraries**:
- `streamlit>=1.31.0` - Web UI framework
- `langchain==0.1.0` - RAG orchestration
- `langchain-openai==0.0.5` - Groq LLM integration
- `openai>=1.10.0` - OpenAI API client (Groq compatible)
- `faiss-cpu==1.13.2` - Vector similarity search
- `sentence-transformers>=2.2.2` - Embedding model loading

**Document Processing**:
- `PyPDF2==3.0.1` - PDF text extraction
- `python-docx==0.8.11` - Word document processing
- `openpyxl==3.1.2` - Excel file handling
- `pandas>=2.0.3` - CSV and data manipulation

**Utilities**:
- `tiktoken>=0.5.1` - Token counting
- `pydantic>=2.4.2` - Data validation
- `numpy>=1.24.3` - Array operations
- `pillow>=10.0.0` - Image handling

### API Reference

**RAGPipeline**:
```python
pipeline = RAGPipeline(use_openai_embeddings=False)
retrieved_docs = pipeline.retrieve(query, top_k=3)
response = pipeline.generate_response(query, retrieved_docs)
```

**AIAgent**:
```python
agent = AIAgent(pipeline)
result = agent.process_query(query, top_k=3)
# Returns: {"response": str, "retrieved_docs": list}
```

**VectorStoreManager**:
```python
store = VectorStoreManager()
store.add_chunks(chunks, embeddings)
results = store.search(query_embedding, top_k=5)
store.save("data/vector_store")
store.clear()
```

---

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ End-to-end RAG system implementation
- ✅ LLM integration and prompt engineering
- ✅ Vector similarity search and semantic retrieval
- ✅ Agent-based AI architecture
- ✅ Production deployment practices
- ✅ Error handling and safety controls
- ✅ Full-stack development (frontend + backend)
- ✅ Cloud deployment (Streamlit Community Cloud)

---

## 📞 Support

**GitHub Repository**: https://github.com/AntonioDaher/ai-agent-rag-system-amd

**Issues**: Open an issue for bug reports or feature requests

**Deployment Questions**: See `STANDALONE_DEPLOYMENT.md`

---

## 📄 License

This project is for educational purposes as part of a capstone project.

---

## 🙏 Acknowledgments

- **Groq AI** for free high-performance LLM API
- **Streamlit** for free cloud hosting
- **LangChain** for RAG framework
- **Hugging Face** for embedding models
- **FAISS** for vector search technology

---

**Built with ❤️ for Enterprise AI Applications**

*Last Updated: February 2026*
