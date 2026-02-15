# Document Chunking Improvements

## Problem
Your PDF was being split into extremely small chunks (0-24 characters), which severely limited retrieval quality. This prevented semantic search from finding relevant content.

## Root Causes
1. **Insufficient chunk size**: Default 500 characters was too small for meaningful context
2. **Poor paragraph extraction**: PDF text extraction resulted in very short segments
3. **Minimal overlap**: 50 character overlap wasn't enough for context continuity

## Solutions Implemented

### 1. **Increased Chunk Size** (500 → 2000 characters)
   - **Impact**: Each chunk now contains ~4x more context
   - **Benefit**: Better semantic meaning and improved retrieval
   - **Location**: `.env` file `CHUNK_SIZE=2000`

### 2. **Increased Chunk Overlap** (50 → 200 characters)
   - **Impact**: Better continuity between chunks
   - **Benefit**: Reduced information loss at chunk boundaries
   - **Location**: `.env` file `CHUNK_OVERLAP=200`

### 3. **Improved PDF Text Extraction**
   - **Change**: Modified PDFProcessor to preserve double newlines between pages
   - **Impact**: Better paragraph detection during chunking
   - **File**: `src/document_processor/processor.py`

### 4. **Dynamic Configuration**
   - **Change**: Server now reads chunk settings from `.env` file
   - **Benefit**: Can adjust chunk size without recompiling
   - **File**: `src/api/server_lite.py`

## Configuration in .env
```env
# Document Chunking Settings (for better retrieval quality)
CHUNK_SIZE=2000      # Characters per chunk (was 500)
CHUNK_OVERLAP=200    # Overlap between chunks (was 50)
```

## Expected Improvements

### Before
- Chunks: 0-24 characters (too small)
- Context loss: High
- Retrieval quality: Poor
- Example: "BASICS OF AI P..." (truncated)

### After
- Chunks: ~2000 characters (meaningful paragraphs)
- Context loss: Minimal (20% overlap)
- Retrieval quality: Excellent
- Example: Full paragraphs with complete sentences

## Testing

### To Test with New Settings:

1. **Delete old vector store** (to clear old chunks):
   ```powershell
   Remove-Item ./data/vector_store -Recurse -Force -ErrorAction SilentlyContinue
   ```

2. **Restart server**:
   ```powershell
   python -m uvicorn src.api.server_lite:app --host 127.0.0.1 --port 9011
   ```

3. **Upload your PDF again**:
   - Use Swagger UI or API call
   - Check chunks created (should be more meaningful)

4. **Test query**:
   ```json
   {
     "query": "What is the name of the institute that is providing the program?",
     "top_k": 3
   }
   ```

## Advanced Configuration

To further customize, adjust these values in `.env`:

```env
# Conservative (smaller chunks, more granular)
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# Aggressive (larger chunks, less fragmented)
CHUNK_SIZE=3000
CHUNK_OVERLAP=300

# For short documents (news, summaries)
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# For dense technical docs (textbooks, research)
CHUNK_SIZE=2500
CHUNK_OVERLAP=250
```

## Files Modified
1. `src/api/server_lite.py` - Now reads chunk settings from config
2. `src/document_processor/processor.py` - Improved PDF text extraction
3. `.env` - Added CHUNK_SIZE and CHUNK_OVERLAP settings

## Next Steps
- Restart the server
- Re-upload your PDF document
- Test queries with improved chunk retrieval
- Adjust CHUNK_SIZE if needed based on your document type
