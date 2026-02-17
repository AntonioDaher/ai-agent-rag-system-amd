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
from src.agents.agent import AgentOrchestrator

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


@st.cache_resource
def initialize_pipeline(groq_api_key: str):
    """Initialize RAG pipeline (cached for performance)"""
    try:
        # Set API key in environment
        os.environ["OPENAI_API_KEY"] = groq_api_key
        os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
        
        # Force settings reload with new API key
        settings.openai_api_key = groq_api_key
        settings.groq_api_key = groq_api_key
        
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
            # Get appropriate processor
            processor = DocumentProcessorFactory.get_processor(tmp_path)
            
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
            pipeline.vector_store_manager.add_documents(chunks, embeddings)
            
            # Save vector store
            vector_store_path = settings.data_path / "vector_store"
            vector_store_path.mkdir(parents=True, exist_ok=True)
            pipeline.vector_store_manager.save(str(vector_store_path))
            
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
        total = pipeline.vector_store_manager.count()
        return {"total_chunks": total, "status": "ok"}
    except:
        return {"total_chunks": 0, "status": "empty"}


def reset_vector_store(pipeline: RAGPipeline):
    """Reset the vector store"""
    try:
        pipeline.vector_store_manager.reset()
        vector_store_path = settings.data_path / "vector_store"
        if vector_store_path.exists():
            import shutil
            shutil.rmtree(vector_store_path)
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
    
    if groq_api_key:
        st.success("✅ API Key configured")
        st.session_state["pipeline"] = initialize_pipeline(groq_api_key)
        
        if st.session_state["pipeline"]:
            # Show vector store stats
            stats = get_vector_store_stats(st.session_state["pipeline"])
            st.metric("Documents in Store", stats["total_chunks"])
    else:
        st.warning("⚠️ Please enter your Groq API key to continue")
        st.info("Get a free API key at [console.groq.com](https://console.groq.com)")
    
    st.divider()
    
    # Model settings
    with st.expander("🔧 Advanced Settings"):
        model_name = st.selectbox(
            "LLM Model",
            options=["llama-3.3-70b-versatile", "llama3-70b-8192", "mixtral-8x7b-32768"],
            index=0
        )
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
        
        if st.session_state["pipeline"]:
            settings.llm_model = model_name
            settings.llm_temperature = temperature


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

# Document Upload Section
if show_upload:
    st.divider()
    st.subheader("2️⃣ Upload Documents")
    
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
    
    query_text = st.text_area(
        "Your question:",
        placeholder=placeholder,
        height=120,
        key="query_text",
        disabled=query_disabled,
    )

with options_col:
    if show_upload:
        top_k = st.slider("Results", min_value=1, max_value=10, value=3, help="Number of relevant chunks to retrieve")
    else:
        top_k = 0
    
    use_agent = st.checkbox("🤖 Use Agent", value=False, help="Use AI agent for complex queries")
    show_details = st.checkbox("📋 Show Details", value=False, help="Show retrieved documents")

# Query buttons
ask_col, clear_col = st.columns([1, 1])

with ask_col:
    ask_clicked = st.button("🔍 Ask", use_container_width=True, type="primary")

with clear_col:
    if st.button("🧹 Clear", use_container_width=True):
        st.session_state["query_text"] = ""
        st.rerun()

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
                    retrieved_docs = pipeline.retrieve(query, top_k=top_k)
                    
                    if use_agent:
                        # Use agent for complex queries
                        agent = AgentOrchestrator(pipeline)
                        response = agent.run(query)
                    else:
                        # Standard RAG response
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
                        agent = AgentOrchestrator(pipeline)
                        response = agent.run(query)
                    else:
                        # Direct LLM call without retrieval
                        response = pipeline.generate_response(query, [])
                    
                    st.success("✅ Answer:")
                    st.markdown(response)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Query error: {str(e)}")

# Footer
st.divider()
st.caption("🚀 Standalone AI Agent RAG System - Powered by Groq AI")
