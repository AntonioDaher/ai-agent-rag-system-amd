"""API models and schemas"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class DocumentUploadRequest(BaseModel):
    """Document upload request"""
    file_name: str
    file_content: str


class QueryRequest(BaseModel):
    """Query request"""
    query: str = Field(..., min_length=3, max_length=5000, description="User query")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    use_agent: bool = Field(default=True, description="Use AI agent for processing")


class DocumentMetadata(BaseModel):
    """Document metadata"""
    file_name: str
    source_file: str
    chunk_index: int
    total_chunks: int
    similarity: Optional[float] = None


class QueryResponse(BaseModel):
    """Query response"""
    query: str
    response: str
    retrieved_docs: Optional[List[Dict]] = None
    doc_count: int
    is_valid_response: Optional[bool] = None
    thoughts: Optional[List[Dict]] = None


class VectorStoreStatsResponse(BaseModel):
    """Vector store statistics response"""
    total_chunks: int
    unique_documents: int
    document_files: List[str]
    dimension: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: str
