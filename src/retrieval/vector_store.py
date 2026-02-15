"""Vector database implementation using FAISS"""
import os
import json
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
import numpy as np
from abc import ABC, abstractmethod

from src.config.logger import setup_logger
from src.config.settings import settings
from src.document_processor.chunker import TextChunk

logger = setup_logger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for stored documents"""
    chunk_id: str
    source_file: str
    chunk_index: int
    total_chunks: int
    start_char: int
    end_char: int
    content: str = ""  # Actual chunk text content


class VectorStore(ABC):
    """Base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> None:
        """Add documents to the store"""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Save the vector store"""
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load the vector store"""
        pass


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store"""
    
    def __init__(self, dimension: int = 384):
        """Initialize FAISS vector store"""
        try:
            import faiss
            self.faiss = faiss
        except ImportError:
            logger.error("faiss-cpu is required for vector storage")
            raise
        
        self.dimension = dimension
        self.index = self.faiss.IndexFlatL2(dimension)
        self.metadata: List[DocumentMetadata] = []
        self.embeddings: np.ndarray = np.empty((0, dimension), dtype=np.float32)
    
    def add_documents(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks to vector store"""
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings provided")
            return
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store metadata
        for chunk in chunks:
            metadata = DocumentMetadata(
                chunk_id=chunk.chunk_id,
                source_file=chunk.source_file,
                chunk_index=chunk.chunk_index,
                total_chunks=chunk.total_chunks,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                content=chunk.content,
            )
            self.metadata.append(metadata)
        
        # Store embeddings
        self.embeddings = np.vstack([self.embeddings, embeddings_array])
        
        logger.info(f"Added {len(chunks)} chunks to vector store. Total: {len(self.metadata)}")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar chunks"""
        query_array = np.array([query_embedding], dtype=np.float32)
        
        distances, indices = self.index.search(query_array, min(top_k, len(self.metadata)))
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                metadata = self.metadata[idx]
                # Convert L2 distance to similarity score
                similarity = 1 / (1 + distance)
                results.append((metadata.chunk_id, float(similarity)))
        
        return results
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Get chunk metadata by ID"""
        for metadata in self.metadata:
            if metadata.chunk_id == chunk_id:
                return asdict(metadata)
        return None
    
    def save(self, path: str) -> None:
        """Save vector store to disk"""
        os.makedirs(path, exist_ok=True)
        
        # Save FAISS index
        index_path = os.path.join(path, "faiss.index")
        self.faiss.write_index(self.index, index_path)
        
        # Save metadata
        metadata_path = os.path.join(path, "metadata.json")
        metadata_dicts = [asdict(m) for m in self.metadata]
        with open(metadata_path, 'w') as f:
            json.dump(metadata_dicts, f, indent=2)
        
        # Save embeddings
        embeddings_path = os.path.join(path, "embeddings.npy")
        np.save(embeddings_path, self.embeddings)
        
        logger.info(f"Saved vector store to {path}")
    
    def load(self, path: str) -> None:
        """Load vector store from disk"""
        if not os.path.exists(path):
            logger.warning(f"Vector store path does not exist: {path}")
            return
        
        # Load FAISS index
        index_path = os.path.join(path, "faiss.index")
        if os.path.exists(index_path):
            self.index = self.faiss.read_index(index_path)
        
        # Load metadata
        metadata_path = os.path.join(path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata_dicts = json.load(f)
                self.metadata = [
                    DocumentMetadata(**m) for m in metadata_dicts
                ]
        
        # Load embeddings
        embeddings_path = os.path.join(path, "embeddings.npy")
        if os.path.exists(embeddings_path):
            self.embeddings = np.load(embeddings_path)
        
        logger.info(f"Loaded vector store from {path} with {len(self.metadata)} chunks")
    
    def get_size(self) -> int:
        """Get number of documents in store"""
        return len(self.metadata)
    
    def get_all_documents(self) -> List[Dict]:
        """Get all document metadata"""
        return [asdict(m) for m in self.metadata]


class VectorStoreManager:
    """Manage vector store operations"""
    
    def __init__(self, dimension: int = 384, vector_store_path: str = None):
        """Initialize vector store manager"""
        self.vector_store = FAISSVectorStore(dimension=dimension)
        self.vector_store_path = vector_store_path or settings.vector_store_path
        
        # Load existing store if it exists
        if os.path.exists(self.vector_store_path):
            self.vector_store.load(self.vector_store_path)
    
    def add_chunks(self, chunks: List[TextChunk], embeddings: List[List[float]]) -> None:
        """Add chunks to vector store"""
        self.vector_store.add_documents(chunks, embeddings)
        # Auto-save after adding
        self.save()
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search vector store"""
        results = self.vector_store.search(query_embedding, top_k)
        
        detailed_results = []
        for chunk_id, similarity in results:
            metadata = self.vector_store.get_chunk_by_id(chunk_id)
            if metadata:
                metadata['similarity'] = similarity
                detailed_results.append(metadata)
        
        return detailed_results
    
    def save(self) -> None:
        """Save vector store"""
        self.vector_store.save(self.vector_store_path)
    
    def load(self) -> None:
        """Load vector store"""
        self.vector_store.load(self.vector_store_path)
    
    def get_statistics(self) -> Dict:
        """Get vector store statistics"""
        documents = self.vector_store.get_all_documents()
        
        # Count unique source files
        source_files = set(doc['source_file'] for doc in documents)
        
        return {
            "total_chunks": self.vector_store.get_size(),
            "unique_documents": len(source_files),
            "document_files": list(source_files),
            "dimension": self.vector_store.dimension,
        }
    
    def clear(self, uploads_dir: str = None) -> None:
        """Clear all documents from the vector store and optionally uploaded files"""
        # Reset the vector store
        dimension = self.vector_store.dimension
        self.vector_store = FAISSVectorStore(dimension=dimension)
        
        # Delete persisted files
        import shutil
        if os.path.exists(self.vector_store_path):
            shutil.rmtree(self.vector_store_path)
            os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Delete uploaded files if uploads_dir is provided
        if uploads_dir and os.path.exists(uploads_dir):
            deleted_count = 0
            error_count = 0
            for filename in os.listdir(uploads_dir):
                file_path = os.path.join(uploads_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted file: {file_path}")
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted directory: {file_path}")
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error deleting {file_path}: {e}")
            logger.info(f"Cleared {uploads_dir} folder: {deleted_count} items deleted, {error_count} errors")
        else:
            logger.warning(f"Uploads directory not found or not provided: {uploads_dir}")
        
        logger.info("Vector store cleared")
