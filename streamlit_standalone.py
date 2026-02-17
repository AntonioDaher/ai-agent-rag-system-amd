"""
Standalone Streamlit AI Agent RAG System
All functionality runs locally - no external API required
"""
import os
import sys
import tempfile
from pathlib import Path
import streamlit as st

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import RAG components
from src.config.logger import setup_logger
from src.config.settings import settings
from src.document_processor.processor import DocumentProcessorFactory
from src.document_processor.chunker import TextChunker
from src.embeddings.embedding import EmbeddingManager
from src.retrieval.vector_store import VectorStoreManager
from src.rag.pipeline import RAGPipeline
from src.agents.agent import AIAgent

logger = setup_logger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="AI Agent RAG System (Standalone)",
    page_icon="📄",
    layout="wide",
)

# Initialize session state
if "pipeline" not in st.session_state:
    st.session_state["pipeline"] = None
if "vector_store_loaded" not in st.session_state:
    st.session_state["vector_store_loaded"] = False
if "total_documents" not in st.session_state:
    st.session_state["total_documents"] = 0
if "uploaded_files_info" not in st.session_state:
    st.session_state["uploaded_files_info"] = []  # Track uploaded files
if "user_decision_made" not in st.session_state:
    st.session_state["user_decision_made"] = False  # Track if user decided on existing files
if "previous_query_mode" not in st.session_state:
    st.session_state["previous_query_mode"] = None  # Track mode changes


@st.cache_resource
def initialize_pipeline(groq_api_key: str, model_name: str = "llama-3.3-70b-versatile"):
    """Initialize RAG pipeline (cached for performance)"""
    try:
        # Set API key in environment
        os.environ["OPENAI_API_KEY"] = groq_api_key
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        
        # Force settings reload with new API key and model
        settings.openai_api_key = groq_api_key
        settings.groq_api_key = groq_api_key
        settings.llm_model = model_name
        
        # Initialize pipeline
        pipeline = RAGPipeline(use_openai_embeddings=False)
        
        # Try to load existing vector store
        try:
            vector_store_path = settings.data_path / "vector_store"
            if vector_store_path.exists():
                pipeline.vector_store_manager.load(str(vector_store_path))
                logger.info("Loaded existing vector store")
        except Exception as e:
            logger.warning(f"Could not load existing vector store: {e}")
        
        return pipeline
    except Exception as e:
        st.error(f"Failed to initialize pipeline: {str(e)}")
        logger.error(f"Pipeline initialization error: {str(e)}")
        return None


def process_uploaded_file(uploaded_file, pipeline: RAGPipeline):
    """Process an uploaded file and add to vector store"""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Get appropriate processor for file extension
            file_extension = Path(uploaded_file.name).suffix.lower().strip('.')
            processor = DocumentProcessorFactory.get_processor(file_extension)
            
            # Extract text
            text_content = processor.process(tmp_path)
            
            # Chunk the text
            chunker = TextChunker(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap
            )
            chunks = chunker.chunk_text(text_content, source_file=uploaded_file.name)
            
            # Generate embeddings
            embeddings = [
                pipeline.embedding_manager.embed_text(chunk.content)
                for chunk in chunks
            ]
            
            # Add to vector store
            pipeline.vector_store_manager.add_chunks(chunks, embeddings)
            
            return True, len(chunks), None
        
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except Exception as e:
        logger.error(f"Error processing file {uploaded_file.name}: {str(e)}")
        return False, 0, str(e)


def get_vector_store_stats(pipeline: RAGPipeline):
    """Get statistics about the vector store"""
    try:
        stats = pipeline.vector_store_manager.get_statistics()
        return {"total_chunks": stats.get("total_chunks", 0), "status": "ok"}
    except:
        return {"total_chunks": 0, "status": "empty"}


def reset_vector_store(pipeline: RAGPipeline):
    """Reset the vector store"""
    try:
        # Get uploads directory path
        uploads_dir = str(settings.uploads_path) if hasattr(settings, 'uploads_path') else None
        
        # Clear vector store (this also handles file deletion)
        pipeline.vector_store_manager.clear(uploads_dir=uploads_dir)
        
        return True, None
    except Exception as e:
        return False, str(e)


# App Title
st.title("🤖 AI Agent RAG System (Standalone)")
st.caption("Upload documents and query using AI - No external server required!")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get API key from Streamlit secrets or user input
    default_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else os.getenv("GROQ_API_KEY", "")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        value=default_key,
        type="password",
        help="Get your free API key from: https://console.groq.com"
    )
    
    st.divider()
    
    # Model settings (before pipeline initialization)
    st.subheader("🔧 Model Settings")
    model_name = st.selectbox(
        "LLM Model",
        options=["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
        index=0,
        help="Choose the AI model for responses"
    )
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="Higher = more creative, Lower = more focused")
    
    st.divider()
    
    # Initialize pipeline with selected model
    if groq_api_key:
        st.success("✅ API Key configured")
        st.session_state["pipeline"] = initialize_pipeline(groq_api_key, model_name)
        
        # Update temperature setting
        if st.session_state["pipeline"]:
            settings.llm_temperature = temperature
            
            # Show vector store stats
            stats = get_vector_store_stats(st.session_state["pipeline"])
            st.metric("Documents in Store", stats["total_chunks"])
    else:
        st.warning("⚠️ Please enter your Groq API key to continue")
        st.info("Get a free API key at [console.groq.com](https://console.groq.com)")


# Main content
if not groq_api_key:
    st.error("🔑 Please enter your Groq API Key in the sidebar to get started")
    st.stop()

if not st.session_state["pipeline"]:
    st.error("❌ Failed to initialize RAG pipeline. Check your API key and try again.")
    st.stop()

pipeline = st.session_state["pipeline"]

# Query Mode Selection
st.subheader("1️⃣ Query Mode")
query_mode = st.radio(
    "Choose your query mode:",
    options=[
        "💬 LLM Direct Query (No documents needed)",
        "📚 RAG Query (Search uploaded documents)",
    ],
    index=0,
    horizontal=True,
)

show_upload = query_mode == "📚 RAG Query (Search uploaded documents)"

# Detect mode change and reset decision flag when switching back to RAG mode
if st.session_state["previous_query_mode"] != query_mode:
    if query_mode == "📚 RAG Query (Search uploaded documents)" and st.session_state["uploaded_files_info"]:
        # User switched back to RAG mode and has previous files - need to prompt again
        st.session_state["user_decision_made"] = False
    st.session_state["previous_query_mode"] = query_mode

# Document Upload Section
if show_upload:
    st.divider()
    st.subheader("2️⃣ Upload Documents")
    
    # Check if there are previously uploaded files and user hasn't decided yet
    has_previous_files = len(st.session_state["uploaded_files_info"]) > 0
    
    if has_previous_files and not st.session_state["user_decision_made"]:
        # Show decision prompt
        st.info("📂 **You have previously uploaded documents.**")
        
        # Show list of previous files
        st.write("**Previously uploaded files:**")
        for file_info in st.session_state["uploaded_files_info"]:
            st.text(f"✓ {file_info['name']} - {file_info['chunks']} chunks")
        
        st.divider()
        st.warning("⚠️ **What would you like to do?**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Continue with existing files", use_container_width=True, type="primary"):
                st.session_state["user_decision_made"] = True
                st.rerun()
        
        with col2:
            if st.button("🗑️ Reset and start fresh", use_container_width=True):
                # Reset everything
                success, error = reset_vector_store(pipeline)
                if success:
                    st.session_state["uploaded_files_info"] = []
                    st.session_state["user_decision_made"] = True
                    st.success("🗑️ Vector store reset successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ Reset failed: {error}")
        
        # Don't show file uploader until user decides
        st.stop()
    
    # User has decided or no previous files - show normal upload interface
    if has_previous_files and st.session_state["user_decision_made"]:
        with st.expander("📁 Current Files in Vector Store", expanded=False):
            for file_info in st.session_state["uploaded_files_info"]:
                st.text(f"✓ {file_info['name']} - {file_info['chunks']} chunks")
    
    upload_col, info_col = st.columns([2, 3])
    
    with upload_col:
        uploaded_files = st.file_uploader(
            "Choose document(s)",
            type=["pdf", "txt", "csv", "xlsx", "docx"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            upload_clicked = st.button("📤 Upload", use_container_width=True, type="primary")
        with button_col2:
            reset_clicked = st.button("🗑️ Reset Store", use_container_width=True)
    
    with info_col:
        st.info(
            """
**📤 Upload**: Process and index documents for searching
            
**🗑️ Reset Store**: Delete all indexed documents (requires confirmation)
            
Supported formats: PDF, TXT, CSV, XLSX, DOCX
            """
        )
    
    # Handle upload
    if upload_clicked:
        if not uploaded_files:
            st.warning("⚠️ Please select one or more files to upload.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            total_chunks = 0
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing: {uploaded_file.name}...")
                
                success, chunks, error = process_uploaded_file(uploaded_file, pipeline)
                
                if success:
                    st.success(f"✅ {uploaded_file.name} - {chunks} chunks indexed")
                    total_chunks += chunks
                    
                    # Store uploaded file info in session state
                    file_info = {
                        "name": uploaded_file.name,
                        "chunks": chunks,
                        "size": uploaded_file.size
                    }
                    # Check if file already exists in the list (avoid duplicates)
                    existing_names = [f["name"] for f in st.session_state["uploaded_files_info"]]
                    if uploaded_file.name not in existing_names:
                        st.session_state["uploaded_files_info"].append(file_info)
                else:
                    st.error(f"❌ {uploaded_file.name} - Error: {error}")
                
                progress_bar.progress((idx + 1) / total_files)
            
            status_text.text(f"✅ Complete! Indexed {total_chunks} chunks from {total_files} files")
            st.balloons()
    
    # Handle reset
    if "reset_confirmation" not in st.session_state:
        st.session_state["reset_confirmation"] = False
    
    if reset_clicked:
        st.session_state["reset_confirmation"] = True
    
    if st.session_state["reset_confirmation"]:
        st.warning("⚠️ **Warning**: This will delete ALL indexed documents!")
        confirm_col1, confirm_col2, _ = st.columns([1, 1, 2])
        
        with confirm_col1:
            if st.button("✅ Confirm Reset", type="primary"):
                success, error = reset_vector_store(pipeline)
                if success:
                    st.success("🗑️ Vector store reset successfully!")
                    st.session_state["reset_confirmation"] = False
                    st.session_state["uploaded_files_info"] = []  # Clear uploaded files info
                    st.session_state["user_decision_made"] = False  # Reset decision flag
                    st.rerun()
                else:
                    st.error(f"❌ Reset failed: {error}")
        
        with confirm_col2:
            if st.button("❌ Cancel"):
                st.session_state["reset_confirmation"] = False
                st.rerun()

# Query Section
st.divider()
query_step = "3️⃣" if show_upload else "2️⃣"
st.subheader(f"{query_step} Ask Your Question")

# Check if documents exist for RAG mode
has_documents = False
if show_upload:
    stats = get_vector_store_stats(pipeline)
    has_documents = stats["total_chunks"] > 0
    
    if not has_documents:
        st.info("📁 No documents indexed yet. Upload documents above to use RAG mode.")

query_col, options_col = st.columns([3, 1])

with query_col:
    if query_mode == "💬 LLM Direct Query (No documents needed)":
        placeholder = "Ask me anything..."
    else:
        placeholder = "Ask about your uploaded documents..." if has_documents else "⚠️ Upload documents first..."
    
    query_disabled = show_upload and not has_documents
    
    # Initialize query text in session state if not exists
    if "query_input" not in st.session_state:
        st.session_state["query_input"] = ""
    
    query_text = st.text_area(
        "Your question:",
        value=st.session_state["query_input"],
        placeholder=placeholder,
        height=120,
        disabled=query_disabled,
    )

with options_col:
    if show_upload:
        top_k = st.slider("Results", min_value=1, max_value=10, value=3, help="Number of relevant chunks to retrieve")
        use_agent = st.checkbox("🤖 Use Agent", value=False, help="Use AI agent for complex queries")
        show_details = st.checkbox("📋 Show Details", value=False, help="Show retrieved documents")
    else:
        top_k = 0
        use_agent = False  # Agent not applicable for direct LLM queries
        show_details = False

# Query buttons
ask_col, clear_col = st.columns([1, 1])

with ask_col:
    ask_clicked = st.button("🔍 Ask", use_container_width=True, type="primary")

with clear_col:
    clear_clicked = st.button("🧹 Clear", use_container_width=True)

# Handle clear button first (before updating session state)
if clear_clicked:
    st.session_state["query_input"] = ""
    st.rerun()

# Update session state with current query text (only if not clearing)
if not clear_clicked:
    st.session_state["query_input"] = query_text

# Process query
if ask_clicked:
    if not query_text.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("🤔 Thinking..."):
            try:
                query = query_text.strip()
                
                # Determine if we need RAG
                if show_upload and has_documents:
                    # RAG Query
                    if use_agent:
                        # Use agent for complex queries (handles retrieval internally)
                        agent = AIAgent(pipeline)
                        result = agent.process_query(query, top_k=top_k)
                        response = result.get('response', '')
                        retrieved_docs = result.get('retrieved_docs', [])
                    else:
                        # Standard RAG response
                        retrieved_docs = pipeline.retrieve(query, top_k=top_k)
                        response = pipeline.generate_response(query, retrieved_docs)
                    
                    # Display response
                    st.success("✅ Answer:")
                    st.markdown(response)
                    
                    # Show details if requested
                    if show_details:
                        st.divider()
                        st.subheader("📚 Retrieved Documents")
                        
                        if not retrieved_docs:
                            st.info("No relevant documents found.")
                        else:
                            for idx, doc in enumerate(retrieved_docs, 1):
                                similarity = doc.get('similarity', 0)
                                source = doc.get('source_file', 'Unknown')
                                chunk_index = doc.get('chunk_index', 0)
                                total_chunks = doc.get('total_chunks', 0)
                                content = doc.get('content', '')
                                
                                with st.expander(f"📄 Document {idx}: {source} (chunk {chunk_index}/{total_chunks}) - Similarity: {similarity:.3f}"):
                                    st.text(content)
                
                else:
                    # Direct LLM Query (no RAG)
                    if use_agent:
                        agent = AIAgent(pipeline)
                        result = agent.process_query(query, top_k=0)
                        response = result.get('response', '')
                    else:
                        # Direct LLM call without retrieval - use custom prompt
                        direct_system_prompt = """You are a helpful and knowledgeable AI assistant.
                        
                        Guidelines:
                        - Answer questions directly and clearly
                        - Use your general knowledge to provide accurate information
                        - Be concise but thorough
                        - If you're unsure about something, say so
                        - Provide helpful context when appropriate"""
                        
                        # Call LLM directly with custom prompt
                        messages = [
                            pipeline.SystemMessage(content=direct_system_prompt),
                            pipeline.HumanMessage(content=query)
                        ]
                        response = pipeline.llm.invoke(messages).content
                    
                    st.success("✅ Answer:")
                    st.markdown(response)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Query error: {str(e)}")

# Footer
st.divider()
st.caption("🚀 Standalone AI Agent RAG System - Powered by Groq AI")
