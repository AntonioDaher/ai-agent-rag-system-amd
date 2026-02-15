"""Embedding generation and management"""
from typing import List, Dict
import numpy as np
from abc import ABC, abstractmethod

from src.config.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)


class EmbeddingModel(ABC):
    """Base class for embedding models"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string"""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple text strings"""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass


class SentenceTransformerEmbedding(EmbeddingModel):
    """Embedding using Sentence Transformers"""
    
    def __init__(self, model_name: str = None):
        """Initialize Sentence Transformer model"""
        self.model_name = model_name or settings.embedding_model
        
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except ImportError:
            logger.error("sentence-transformers is required for embedding")
            raise
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text"""
        embeddings = self.model.encode([text])
        return embeddings[0].tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()


class OpenAIEmbedding(EmbeddingModel):
    """Embedding using OpenAI API"""
    
    def __init__(self, api_key: str = None):
        """Initialize OpenAI embedding client"""
        self.api_key = api_key or settings.openai_api_key
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.model = "text-embedding-3-small"
            logger.info("Initialized OpenAI embedding client")
        except ImportError:
            logger.error("openai package is required")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Embed a single text via OpenAI"""
        embeddings = self.embed_texts([text])
        return embeddings[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple texts via OpenAI"""
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            embeddings = [item.embedding for item in response.data]
            return embeddings
        except Exception as e:
            logger.error(f"Error getting embeddings from OpenAI: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        # text-embedding-3-small has 512 dimensions
        return 512


class EmbeddingManager:
    """Manage embedding operations"""
    
    def __init__(self, use_openai: bool = False):
        """Initialize embedding manager"""
        if use_openai:
            self.model = OpenAIEmbedding()
        else:
            self.model = SentenceTransformerEmbedding()
        
        self.embedding_cache: Dict[str, List[float]] = {}
    
    def embed_text(self, text: str, use_cache: bool = True) -> List[float]:
        """Embed text with optional caching"""
        if use_cache and text in self.embedding_cache:
            return self.embedding_cache[text]
        
        embedding = self.model.embed_text(text)
        
        if use_cache:
            self.embedding_cache[text] = embedding
        
        return embedding
    
    def embed_texts(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """Embed multiple texts"""
        embeddings = []
        texts_to_embed = []
        text_indices = []
        
        for i, text in enumerate(texts):
            if use_cache and text in self.embedding_cache:
                embeddings.append(None)
            else:
                embeddings.append(None)
                texts_to_embed.append(text)
                text_indices.append(i)
        
        if texts_to_embed:
            new_embeddings = self.model.embed_texts(texts_to_embed)
            
            for i, idx in enumerate(text_indices):
                embeddings[idx] = new_embeddings[i]
                if use_cache:
                    self.embedding_cache[texts[idx]] = new_embeddings[i]
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_dimension()
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embedding_cache.clear()
        logger.info("Cleared embedding cache")
