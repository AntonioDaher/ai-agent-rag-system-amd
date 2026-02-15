"""Main API server"""
import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from src.config.settings import settings
from src.config.logger import setup_logger
from src.api.models import (
    QueryRequest, QueryResponse, VectorStoreStatsResponse, HealthResponse
)
from src.document_processor.processor import DocumentProcessorFactory, extract_metadata
from src.document_processor.chunker import TextChunker
from src.embeddings.embedding import EmbeddingManager
from src.retrieval.vector_store import VectorStoreManager
from src.rag.pipeline import RAGPipeline
from src.agents.agent import AIAgent
from src.safety.guards import SafetyManager

logger = setup_logger(__name__)

# Initialize app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Generative AI-powered enterprise document Q&A system with autonomous agents"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    embedding_manager = EmbeddingManager()
    rag_pipeline = RAGPipeline()
    ai_agent = AIAgent(rag_pipeline)
    safety_manager = SafetyManager()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {str(e)}")
    raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a document"""
    try:
        # Validate file
        file_ext = Path(file.filename).suffix.lower().strip('.')
        allowed = settings.get_allowed_extensions_list()
        
        if file_ext not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type .{file_ext} not allowed. Allowed: {', '.join(allowed)}"
            )
        
        # Create uploads directory if it doesn't exist
        os.makedirs(settings.uploads_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(settings.uploads_path, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename}")
        
        return {
            "status": "success",
            "message": f"File {file.filename} uploaded successfully",
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process-document")
async def process_document(file_path: str):
    """Process an uploaded document and add to vector store"""
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        logger.info(f"Processing document: {file_path}")
        
        # Step 1: Extract text from document
        text = DocumentProcessorFactory.process_document(file_path)
        logger.info(f"Extracted {len(text)} characters from {file_path}")
        
        # Step 2: Chunk the text
        chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        chunks = chunker.chunk_text(text, source_file=os.path.basename(file_path))
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 3: Generate embeddings
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = embedding_manager.embed_texts(chunk_texts)
        logger.info(f"Generated embeddings for {len(embeddings)} chunks")
        
        # Step 4: Add to vector store
        rag_pipeline.vector_store_manager.add_chunks(chunks, embeddings)
        logger.info(f"Added {len(chunks)} chunks to vector store")
        
        return {
            "status": "success",
            "message": f"Document processed successfully",
            "chunks_created": len(chunks),
            "file_path": file_path
        }
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents using RAG and agents"""
    try:
        # Validate query
        is_valid, error_msg = safety_manager.validate_and_sanitize_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Processing query: {request.query}")
        
        if request.use_agent:
            # Use AI Agent for processing
            result = ai_agent.process_query(
                query=request.query,
                top_k=request.top_k,
                return_thoughts=True
            )
            
            if result["status"] != "success":
                raise HTTPException(status_code=500, detail=result.get("error"))
            
            # Check response quality
            quality_check = safety_manager.check_response_quality(
                result["response"],
                result["retrieved_docs"]
            )
            
            return QueryResponse(
                query=request.query,
                response=result["response"],
                retrieved_docs=result["retrieved_docs"],
                doc_count=len(result["retrieved_docs"]),
                is_valid_response=result.get("is_valid_response"),
                thoughts=result.get("thoughts")
            )
        else:
            # Use RAG pipeline directly
            result = rag_pipeline.query(
                query=request.query,
                top_k=request.top_k
            )
            
            return QueryResponse(
                query=request.query,
                response=result["response"],
                retrieved_docs=result["retrieved_docs"],
                doc_count=result["doc_count"]
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/vector-store/stats", response_model=VectorStoreStatsResponse)
async def get_vector_store_stats():
    """Get vector store statistics"""
    try:
        stats = rag_pipeline.get_vector_store_stats()
        return VectorStoreStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vector-store/clear")
async def clear_vector_store():
    """Clear vector store"""
    try:
        logger.warning("Clearing vector store")
        # Reinitialize vector store
        global rag_pipeline, ai_agent
        rag_pipeline = RAGPipeline()
        ai_agent = AIAgent(rag_pipeline)
        
        return {
            "status": "success",
            "message": "Vector store cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
