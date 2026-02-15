"""Test script to verify improved chunking"""
import sys
sys.path.insert(0, 'c:\\Users\\HP SPECTRE\\Downloads\\Edureka (Final Project)\\ai_agent_rag_system')

from src.document_processor.processor import DocumentProcessorFactory
from src.document_processor.chunker import TextChunker
from pathlib import Path

# Path to the PDF
pdf_path = r"c:\Users\HP SPECTRE\Downloads\Edureka (Final Project)\ai_agent_rag_system\uploads\BASICS OF AI PROGRAM (IMP).pdf"

if Path(pdf_path).exists():
    print("=" * 70)
    print("CHUNKING QUALITY TEST")
    print("=" * 70)
    
    # Extract text
    text = DocumentProcessorFactory.process_document(pdf_path)
    print(f"\n✓ PDF extracted: {len(text)} characters total")
    print(f"  Preview: {text[:200]}...\n")
    
    # Test with old settings (500 chars)
    print("-" * 70)
    print("OLD SETTINGS (chunk_size=500, overlap=50):")
    print("-" * 70)
    chunker_old = TextChunker(chunk_size=500, chunk_overlap=50)
    chunks_old = chunker_old.chunk_text(text, "test.pdf")
    
    print(f"Total chunks: {len(chunks_old)}")
    for i, chunk in enumerate(chunks_old[:3]):  # Show first 3
        print(f"\nChunk {i} ({len(chunk.content)} chars):")
        print(f"  [{chunk.start_char}-{chunk.end_char}]: {chunk.content[:80]}...")
    
    # Test with new settings (2000 chars)
    print("\n" + "-" * 70)
    print("NEW SETTINGS (chunk_size=2000, overlap=200):")
    print("-" * 70)
    chunker_new = TextChunker(chunk_size=2000, chunk_overlap=200)
    chunks_new = chunker_new.chunk_text(text, "test.pdf")
    
    print(f"Total chunks: {len(chunks_new)}")
    for i, chunk in enumerate(chunks_new[:3]):  # Show first 3
        print(f"\nChunk {i} ({len(chunk.content)} chars):")
        print(f"  [{chunk.start_char}-{chunk.end_char}]: {chunk.content[:100]}...")
    
    print("\n" + "=" * 70)
    print("IMPROVEMENT SUMMARY:")
    print("=" * 70)
    avg_old = sum(len(c.content) for c in chunks_old) / len(chunks_old)
    avg_new = sum(len(c.content) for c in chunks_new) / len(chunks_new)
    
    print(f"Average chunk size OLD: {avg_old:.0f} characters")
    print(f"Average chunk size NEW: {avg_new:.0f} characters")
    print(f"Improvement factor: {avg_new/avg_old:.1f}x larger")
    print(f"\nChunks reduced from {len(chunks_old)} to {len(chunks_new)}")
    print("✓ Better context preservation with fewer, larger chunks")
    
else:
    print(f"PDF not found at: {pdf_path}")
