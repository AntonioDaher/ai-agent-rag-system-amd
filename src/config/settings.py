"""Configuration settings for the AI Agent RAG System"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application metadata
    app_name: str = "AI Agent RAG System"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Groq Configuration (Free LLM API)
    groq_api_key: str = ""
    
    # LLM Configuration
    llm_model: str = "gpt-3.5-turbo"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    # Vector Database Configuration
    vector_db_type: str = "faiss"
    vector_store_path: str = "./data/vector_store"
    embedding_model: str = "intfloat/multilingual-e5-small"  # Supports 100+ languages with excellent cross-lingual retrieval
    
    # Document Processing Configuration
    max_upload_size_mb: int = 100
    allowed_extensions: str = "pdf,txt,csv,xlsx,docx"
    chunk_size: int = 500
    chunk_overlap: int = 50
    
    # Agent Configuration
    agent_timeout_seconds: int = 60
    max_agent_iterations: int = 10
    
    # Paths
    base_path: Path = Path(__file__).parent.parent.parent
    data_path: Path = Path(__file__).parent.parent.parent / "data"
    uploads_path: Path = Path(__file__).parent.parent.parent / "data" / "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env
    
    def get_allowed_extensions_list(self) -> list:
        """Parse comma-separated extensions into a list"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]


# Global settings instance
settings = Settings()
