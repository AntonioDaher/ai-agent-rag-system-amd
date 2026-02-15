"""Lightweight API server for testing - avoids Fortran library issues"""
import os
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

os.environ['OPENBLAS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# Load .env file explicitly
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

from fastapi import Depends, FastAPI, Header, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime

# Create app
app = FastAPI(
    title="AI Agent RAG System",
    description="Enterprise Document Q&A with Autonomous Agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize (basic, no heavy models yet)
from src.config.logger import setup_logger
logger = setup_logger(__name__)
logger.info("Initializing AI Agent RAG System...")


def require_api_key(
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None),
) -> None:
    expected_key = os.getenv("RAG_API_KEY")
    if not expected_key:
        return
    bearer_key = None
    if authorization and authorization.lower().startswith("bearer "):
        bearer_key = authorization.split(" ", 1)[1].strip()
    provided_key = bearer_key or x_api_key
    if not provided_key or provided_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


_rate_limit_window_sec = 60
_rate_limit_max = int(os.getenv("RAG_RATE_LIMIT_PER_MIN", "60"))
_rate_limit_store: dict[str, deque] = defaultdict(deque)


def enforce_security(request: Request) -> None:
    allowed_ips = os.getenv("RAG_ALLOWED_IPS", "").strip()
    if allowed_ips:
        allowed_set = {ip.strip() for ip in allowed_ips.split(",") if ip.strip()}
        client_ip = request.client.host if request.client else ""
        if client_ip not in allowed_set:
            raise HTTPException(status_code=403, detail="IP not allowed")

    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    q = _rate_limit_store[client_ip]
    while q and now - q[0] > _rate_limit_window_sec:
        q.popleft()
    if len(q) >= _rate_limit_max:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    q.append(now)

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "message": "AI Agent RAG System is operational"
    }

@app.get("/vector-store/stats")
async def vector_store_stats():
    """Get vector store statistics"""
    try:
        with open("./data/vector_store/metadata.json", "r") as f:
            metadata = json.load(f)

        # metadata.json may be a dict with 'chunks' key (old format) or a list (current format)
        if isinstance(metadata, dict) and "chunks" in metadata:
            metadata_list = metadata.get("chunks", [])
        elif isinstance(metadata, list):
            metadata_list = metadata
        else:
            metadata_list = []

        total_chunks = len(metadata_list)
        unique_documents = len(set(c.get("source_file") for c in metadata_list))
        return {
            "total_chunks": total_chunks,
            "unique_documents": unique_documents,
            "dimension": 384,
            "status": "active"
        }
    except Exception as e:
        return {
            "total_chunks": 0,
            "unique_documents": 0,
            "dimension": 384,
            "status": "no_data",
            "message": str(e)
        }

@app.delete("/vector-store/reset")
async def reset_vector_store(
    request: Request,
    _: None = Depends(require_api_key),
):
    """Reset/clear all documents from the vector store and uploaded files"""
    enforce_security(request)
    
    try:
        from src.retrieval.vector_store import VectorStoreManager
        
        uploads_dir = "./uploads"
        vector_store_manager = VectorStoreManager(dimension=384)
        vector_store_manager.clear(uploads_dir=uploads_dir)
        
        return {
            "status": "success",
            "message": "Vector store and uploaded files have been completely reset.",
            "total_chunks": 0,
            "unique_documents": 0,
            "uploads_cleared": True
        }
    except Exception as e:
        logger.error(f"Failed to reset vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset vector store: {str(e)}")

@app.post("/upload")
async def upload_file(
    file: UploadFile,
    request: Request,
    _: None = Depends(require_api_key),
):
    enforce_security(request)
    """Upload a document (PDF, TXT, CSV, XLSX)"""
    import os
    from pathlib import Path
    
    # Create uploads directory
    uploads_dir = "./uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(uploads_dir, file.filename)
    content = await file.read()
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Try to process with full system
    try:
        from src.document_processor.processor import DocumentProcessorFactory
        from src.document_processor.chunker import TextChunker
        from src.retrieval.vector_store import VectorStoreManager
        from src.embeddings.embedding import EmbeddingManager
        
        # Process document using correct method
        text = DocumentProcessorFactory.process_document(file_path)
        
        # Use configured chunk size for better retrieval
        from src.config.settings import Settings
        config = Settings()
        chunker = TextChunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
        chunks = chunker.chunk_text(text, source_file=file.filename)
        
        embedding_manager = EmbeddingManager()
        vector_store = VectorStoreManager(dimension=384)
        
        # Get embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = embedding_manager.embed_text(chunk.content)
            embeddings.append(embedding)
        
        # Add all chunks at once
        vector_store.add_chunks(chunks, embeddings)
        
        return {
            "status": "Document uploaded and processed successfully",
            "filename": file.filename,
            "file_size": len(content),
            "chunks_created": len(chunks),
            "message": "Document is now searchable. Use /query to ask questions."
        }
    except Exception as e:
        return {
            "status": "Document uploaded (lite mode)",
            "filename": file.filename,
            "file_size": len(content),
            "message": f"Uploaded but not fully processed. Full features available with full server.",
            "note": str(e)
        }

@app.post("/process-document")
async def process_document(file_path: str = None):
    """Process an uploaded document"""
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path required")
    
    return {
        "status": "processing",
        "file_path": file_path,
        "message": "Document processing initiated"
    }

@app.post("/query")
async def query(
    query_request: dict,
    request: Request,
    _: None = Depends(require_api_key),
):
    enforce_security(request)
    """Query the system
    
    Request body:
    {
        "query": "Your question here",
        "top_k": 3,
        "use_agent": false
    }
    """
    if not query_request:
        raise HTTPException(status_code=400, detail="Request body required")
    
    query_text = query_request.get("query")
    top_k = query_request.get("top_k", 3)
    use_agent = query_request.get("use_agent", False)
    
    if not query_text:
        raise HTTPException(status_code=400, detail="query parameter required")
    
    try:
        # Use Groq API directly with requests (no extra package)
        import requests
        import os
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "your_groq_api_key_here":
            return {
                "query": query_text,
                "response": "ERROR: GROQ_API_KEY not set. Get free key at https://console.groq.com",
                "retrieved_docs": [],
                "doc_count": 0,
                "is_valid_response": False,
                "note": "Missing Groq API key - add to .env file"
            }
        
        # Try to retrieve from vector store if available
        retrieved_docs = []
        try:
            from src.embeddings.embedding import EmbeddingManager
            from src.retrieval.vector_store import VectorStoreManager
            
            embedding_manager = EmbeddingManager()
            vector_store_manager = VectorStoreManager(dimension=384)
            
            query_embedding = embedding_manager.embed_text(query_text)
            retrieved_docs = vector_store_manager.search(query_embedding, top_k)
        except:
            pass  # No documents uploaded yet, that's okay
        
        # Build context from retrieved documents (include actual chunk text)
        context = ""
        doc_details = []
        if retrieved_docs:
            context = "Retrieved Documents:\n"
            for i, doc in enumerate(retrieved_docs, 1):
                # doc is a dict with metadata and should include 'content'
                doc_text = doc.get('content', '') if isinstance(doc, dict) else ''
                source = doc.get('source_file', 'unknown') if isinstance(doc, dict) else 'unknown'
                similarity = doc.get('similarity', 0.0) if isinstance(doc, dict) else 0.0
                # Log a short excerpt for debugging (first 200 chars)
                logger.info(f"Retrieved doc {i} from {source} (similarity={similarity:.3f}): {doc_text[:200]}")
                context += f"[Document {i}] ({source}, similarity={similarity:.3f}): {doc_text[:2000]}...\n"
                doc_details.append(doc_text)
        
        # Call Groq API directly with enhanced prompt
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build enhanced prompt with explicit instructions
        if context:
            prompt = f"""You are an expert at extracting information from documents.

{context}

IMPORTANT: Carefully read the above documents and extract the exact information requested.

Question: {query_text}

Instructions:
1. Search through all provided documents for the answer
2. If the answer is in the documents, provide it directly with confidence
3. If the information cannot be found, clearly state that
4. Do not make up information that is not in the documents
5. Look for names, entities, and specific details requested

Answer:"""
        else:
            prompt = f"Answer this question: {query_text}"
        
        payload = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "model": "llama-3.3-70b-versatile",
            "temperature": 0.7,
            "max_tokens": 1024
        }
        
        # Get response from Groq API
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            return {
                "query": query_text,
                "response": f"API Error: {response.status_code} - {response.text}",
                "retrieved_docs": [],
                "doc_count": 0,
                "is_valid_response": False,
                "note": "Check your Groq API key at https://console.groq.com"
            }
        
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        
        return {
            "query": query_text,
            "response": ai_response,
            "retrieved_docs": retrieved_docs if retrieved_docs else [],
            "doc_count": len(retrieved_docs),
            "is_valid_response": True,
            "thoughts": ["Retrieve", "Generate"],
            "llm_model": "Groq llama-3.3-70b-versatile (Free)"
        }
    except Exception as e:
        # Return error with helpful message
        return {
            "query": query_text,
            "response": f"Error: {str(e)}",
            "retrieved_docs": [],
            "doc_count": 0,
            "is_valid_response": False,
            "note": f"Troubleshoot: Check GROQ_API_KEY in .env file"
        }

@app.get("/")
async def root():
    """Root endpoint - redirect to docs"""
    return {
        "message": "AI Agent RAG System API",
        "docs": "/docs",
        "health": "/health",
        "status": "operational"
    }

print("✓ Server initialized successfully")
print("✓ Running at http://127.0.0.1:9011")
print("✓ API Documentation: http://127.0.0.1:9011/docs")
