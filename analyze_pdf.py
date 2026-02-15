"""Search PDF for institute information"""
import sys
import io
# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.document_processor.processor import DocumentProcessorFactory
from src.document_processor.chunker import TextChunker
from pathlib import Path

pdf_path = r'uploads\BASICS OF AI PROGRAM (IMP).pdf'

if Path(pdf_path).exists():
    text = DocumentProcessorFactory.process_document(pdf_path)
    
    print("=" * 80)
    print("PDF CONTENT ANALYSIS")
    print("=" * 80)
    print(f"\nTotal text length: {len(text)} characters\n")
    
    # Show first part
    print("FIRST 1500 CHARACTERS:")
    print("-" * 80)
    print(text[:1500])
    print("\n")
    
    # Search for keywords
    keywords = ['institute', 'university', 'college', 'edureka', 'academy', 'by', 'provided by']
    
    print("KEYWORD SEARCH:")
    print("-" * 80)
    for keyword in keywords:
        if keyword.lower() in text.lower():
            idx = text.lower().find(keyword.lower())
            start = max(0, idx - 150)
            end = min(len(text), idx + 300)
            print(f"\n✓ Found '{keyword}' at position {idx}:")
            print(text[start:end])
            print()
        else:
            print(f"✗ '{keyword}' not found")
    
    # Show chunks
    print("\n" + "=" * 80)
    print("CHUNKS CREATED (7 chunks):")
    print("=" * 80)
    chunker = TextChunker(chunk_size=2000, chunk_overlap=200)
    chunks = chunker.chunk_text(text, "test.pdf")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i}: chars {chunk.start_char}-{chunk.end_char} ({len(chunk.content)} chars)")
        print("-" * 80)
        print(chunk.content[:300] + "...")
else:
    print(f"PDF not found at {pdf_path}")
