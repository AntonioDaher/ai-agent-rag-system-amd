"""Text chunking module for semantic search preparation"""
from typing import List
from dataclasses import dataclass
from src.config.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class TextChunk:
    """Represents a text chunk with metadata"""
    content: str
    chunk_id: str
    source_file: str
    chunk_index: int
    total_chunks: int
    start_char: int
    end_char: int


class TextChunker:
    """Split text into semantically meaningful chunks"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunker
        
        Args:
            chunk_size: Characters per chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, source_file: str = "unknown") -> List[TextChunk]:
        """
        Split text into chunks
        
        Args:
            text: Text to chunk
            source_file: Source file name for metadata
            
        Returns:
            List of TextChunk objects
        """
        chunks = []
        
        # Split by paragraphs first for semantic coherence
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        char_count = 0
        chunk_index = 0
        start_char = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph exceeds chunk size and we have content
            if char_count + len(paragraph) > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = current_chunk.strip()
                if chunk_text:
                    chunks.append(
                        TextChunk(
                            content=chunk_text,
                            chunk_id=f"{source_file}_chunk_{chunk_index}",
                            source_file=source_file,
                            chunk_index=chunk_index,
                            total_chunks=0,  # Will update later
                            start_char=start_char,
                            end_char=start_char + len(chunk_text)
                        )
                    )
                    chunk_index += 1
                
                # Add overlap
                words = current_chunk.split()
                overlap_words = int(len(words) * (self.chunk_overlap / self.chunk_size))
                current_chunk = ' '.join(words[-overlap_words:]) + "\n\n" if overlap_words > 0 else ""
                char_count = len(current_chunk)
                start_char = start_char + len(chunk_text) - len(current_chunk)
            
            current_chunk += paragraph + "\n\n"
            char_count += len(paragraph) + 2
        
        # Add final chunk
        if current_chunk.strip():
            chunk_text = current_chunk.strip()
            chunks.append(
                TextChunk(
                    content=chunk_text,
                    chunk_id=f"{source_file}_chunk_{chunk_index}",
                    source_file=source_file,
                    chunk_index=chunk_index,
                    total_chunks=0,
                    start_char=start_char,
                    end_char=start_char + len(chunk_text)
                )
            )
        
        # Update total_chunks for all chunks
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        logger.info(f"Chunked '{source_file}' into {len(chunks)} chunks")
        return chunks
    
    def chunk_text_by_size(self, text: str, source_file: str = "unknown") -> List[TextChunk]:
        """
        Split text by fixed size with overlap
        
        Args:
            text: Text to chunk
            source_file: Source file name for metadata
            
        Returns:
            List of TextChunk objects
        """
        chunks = []
        chunk_index = 0
        
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            end = min(i + self.chunk_size, len(text))
            chunk_text = text[i:end].strip()
            
            if chunk_text:
                chunks.append(
                    TextChunk(
                        content=chunk_text,
                        chunk_id=f"{source_file}_chunk_{chunk_index}",
                        source_file=source_file,
                        chunk_index=chunk_index,
                        total_chunks=0,
                        start_char=i,
                        end_char=end
                    )
                )
                chunk_index += 1
            
            if end >= len(text):
                break
        
        # Update total_chunks
        total = len(chunks)
        for chunk in chunks:
            chunk.total_chunks = total
        
        logger.info(f"Chunked '{source_file}' into {len(chunks)} fixed-size chunks")
        return chunks
