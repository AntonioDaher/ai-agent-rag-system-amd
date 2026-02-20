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
    page_title="AI Agent RAG System",
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
if "widget_refresh_counter" not in st.session_state:
    st.session_state["widget_refresh_counter"] = 0  # Force widget refresh when cleared
if "previous_model" not in st.session_state:
    st.session_state["previous_model"] = None  # Track model changes
if "vector_store_reset" not in st.session_state:
    st.session_state["vector_store_reset"] = False  # Track if vector store was reset on init
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # Sequential chat flow
if "conversation_memory_enabled" not in st.session_state:
    st.session_state["conversation_memory_enabled"] = True  # Toggle ON/OFF (default ON)


@st.cache_resource(show_spinner=False)
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
        
        # Don't load existing vector store - will be reset on page load
        
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


def render_chat_history():
    """Render chat messages in sequential conversation flow."""
    if not st.session_state["chat_history"]:
        st.info("💬 Start the conversation by asking a question below.")
        return

    for message in st.session_state["chat_history"]:
        role = message.get("role", "assistant")
        content = message.get("content", "")

        with st.chat_message(role):
            st.markdown(content)

            retrieved_docs = message.get("retrieved_docs", [])
            show_details = message.get("show_details", False)

            if role == "assistant" and show_details:
                with st.expander("📚 Retrieved Documents", expanded=False):
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


def build_contextual_query(current_query: str, max_messages: int = 6, max_chars_per_message: int = 600) -> str:
    """Build query with recent chat context when memory is enabled."""
    if not st.session_state.get("conversation_memory_enabled", False):
        return current_query

    history = st.session_state.get("chat_history", [])
    if not history:
        return current_query

    recent_messages = history[-max_messages:]
    formatted_history = []

    for msg in recent_messages:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if len(content) > max_chars_per_message:
            content = content[:max_chars_per_message] + "..."
        formatted_history.append(f"{role}: {content}")

    if not formatted_history:
        return current_query

    return (
        "Use the recent conversation to interpret and answer the current question.\\n\\n"
        "Conversation History:\\n"
        + "\\n".join(formatted_history)
        + f"\\n\\nCurrent Question: {current_query}\\n"
        "Answer the current question directly and clearly."
    )


def build_rag_system_prompt(max_messages: int = 6, max_chars_per_message: int = 600) -> str:
    """Build RAG system prompt with optional conversation memory context."""
    base_prompt = """You are an intelligent assistant that answers questions based on provided documents.
            
            Guidelines:
            - Answer questions using only the information from the provided documents
            - Be clear and concise in your responses
            - If the information is not in the documents, clearly state that
            - Cite the document and chunk number when relevant"""

    if not st.session_state.get("conversation_memory_enabled", False):
        return base_prompt

    history = st.session_state.get("chat_history", [])
    if not history:
        return base_prompt

    recent_messages = history[-max_messages:]
    formatted_history = []

    for msg in recent_messages:
        role = "User" if msg.get("role") == "user" else "Assistant"
        content = (msg.get("content") or "").strip()
        if not content:
            continue
        if len(content) > max_chars_per_message:
            content = content[:max_chars_per_message] + "..."
        formatted_history.append(f"{role}: {content}")

    if not formatted_history:
        return base_prompt

    return (
        f"{base_prompt}\\n\\n"
        "Conversation context from previous turns (use only to resolve references; "
        "do not override document evidence):\\n"
        + "\\n".join(formatted_history)
    )


# App Title
st.title("🤖 AI Agent RAG System")
st.caption("Direct LLM Query or RAG Query")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Get default API key from Streamlit secrets or environment
    default_key = st.secrets.get("GROQ_API_KEY", "") if hasattr(st, "secrets") else os.getenv("GROQ_API_KEY", "")
    
    # Checkbox to enable custom API key input
    use_custom_api = st.checkbox(
        "🔑 Use Custom API Key",
        value=False,
        help="Enable to enter your own Groq API key"
    )
    
    # Show API key input only if checkbox is checked
    if use_custom_api:
        groq_api_key = st.text_input(
            "GROQ API Key",
            value="",
            type="password",
            placeholder="Enter your Groq API key",
            help="Get your free API key from: https://console.groq.com"
        )
    else:
        # Use default key from secrets/environment
        groq_api_key = default_key
        # Display greyed out info
        st.text_input(
            "GROQ API Key",
            value="Using default API key" if default_key else "",
            type="password",
            disabled=True,
            help="Enable 'Use Custom API Key' above to enter your own key"
        )
    
    st.divider()
    
    # Model settings (before pipeline initialization)
    st.subheader("🔧 Model Settings")
    model_name = st.selectbox(
        "LLM Model",
        options=[
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant"
        ],
        index=0,
        help="Choose the AI model for responses"
    )
    
    # Reset query input when model changes
    if st.session_state["previous_model"] != model_name:
        st.session_state["query_input"] = ""
        st.session_state["widget_refresh_counter"] += 1
        st.session_state["previous_model"] = model_name
    
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1, help="Higher = more creative, Lower = more focused")
    
    st.divider()
    
    # Initialize pipeline with selected model
    if groq_api_key:
        st.success("✅ API Key configured")
        
        # Show initialization spinner with custom message
        with st.spinner("⚙️ Initialization..."):
            st.session_state["pipeline"] = initialize_pipeline(groq_api_key, model_name)
        
        # Update temperature setting
        if st.session_state["pipeline"]:
            settings.llm_temperature = temperature
            
            # Reset vector store on first load/page refresh
            if not st.session_state["vector_store_reset"]:
                try:
                    st.session_state["pipeline"].vector_store_manager.clear()
                    st.session_state["uploaded_files_info"] = []
                    st.session_state["user_decision_made"] = False
                    st.session_state["vector_store_reset"] = True
                    logger.info("Vector store reset on page initialization")
                except Exception as e:
                    logger.warning(f"Could not reset vector store: {e}")
            
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
        "💬 LLM Direct Query (No Uploads)",
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
    # Reset query input and increment widget counter when switching modes
    st.session_state["query_input"] = ""
    st.session_state["chat_history"] = []
    st.session_state["widget_refresh_counter"] += 1
    st.session_state["previous_query_mode"] = query_mode

# Document Upload Section
if show_upload:
    st.divider()
    st.subheader("2️⃣ Upload(s)")
    
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
            "Choose document(s) / file(s)",
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
            
            # Mark decision as made so prompt doesn't show again until mode switch
            st.session_state["user_decision_made"] = True
            
            # Save vector store to persist changes
            try:
                vector_store_path = settings.data_path / "vector_store"
                pipeline.vector_store_manager.save(str(vector_store_path))
            except Exception as e:
                logger.warning(f"Could not save vector store: {e}")
            
            # Show success animation
            st.balloons()
            
            # Small delay to allow balloons animation before rerun
            import time
            time.sleep(1)
            
            # Trigger rerun to refresh the UI and show newly uploaded files in the dropdown
            st.rerun()
    
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
st.subheader(f"{query_step} Querying")

st.subheader("💬 Conversation")
render_chat_history()

# Check if documents exist for RAG mode - must be done every time
has_documents = False
if show_upload:
    stats = get_vector_store_stats(pipeline)
    total_chunks = stats.get("total_chunks", 0)
    has_documents = total_chunks > 0
    
    # Show clear warning when no documents
    if not has_documents:
        st.error("🚫 **RAG Query requires documents!** Please upload documents above first.")

# Ask button state
if show_upload and not has_documents:
    ask_button_disabled = True
    button_help = "Upload documents first to enable RAG queries"
else:
    ask_button_disabled = False
    button_help = None

query_col, options_col = st.columns([3, 1])

with query_col:
    # Determine placeholder and disabled state based on mode
    if query_mode == "💬 LLM Direct Query (No Uploads)":
        placeholder = "Ask me anything..."
        query_disabled = False
    else:
        # RAG mode
        if has_documents:
            placeholder = "Ask about your uploaded documents..."
            query_disabled = False
        else:
            placeholder = "⚠️ Please upload documents first to enable RAG query..."
            query_disabled = True
    
    # Initialize query text in session state if not exists
    if "query_input" not in st.session_state:
        st.session_state["query_input"] = ""
    
    with st.form(key=f"query_form_{st.session_state['widget_refresh_counter']}"):
        # Ctrl+Enter submits this form
        query_text = st.text_area(
            "Your question:",
            value=st.session_state["query_input"],
            placeholder=placeholder,
            height=120,
            disabled=query_disabled,
            key=f"query_text_area_{st.session_state['widget_refresh_counter']}",
            help="Text input is disabled until documents are uploaded" if query_disabled else None
        )

        ask_clicked = st.form_submit_button(
            "🔍 Ask",
            use_container_width=True,
            type="primary",
            disabled=ask_button_disabled,
            help=button_help
        )

with options_col:
    memory_toggle = st.toggle(
        "🧠 Conversation Memory",
        value=st.session_state["conversation_memory_enabled"],
        help="ON: Use recent chat turns as context. OFF: Treat each question independently."
    )
    st.session_state["conversation_memory_enabled"] = memory_toggle

    if show_upload:
        # Explicitly disable all options when no documents
        is_disabled = not has_documents
        top_k = st.slider(
            "Results", 
            min_value=1, 
            max_value=10, 
            value=3, 
            help="Disabled: Upload documents first" if is_disabled else "Number of relevant chunks to retrieve",
            disabled=is_disabled
        )
        use_agent = st.checkbox(
            "🤖 Use Agent", 
            value=False, 
            help="Disabled: Upload documents first" if is_disabled else "Use AI agent for complex queries",
            disabled=is_disabled
        )
        show_details = st.checkbox(
            "📋 Show Details", 
            value=False, 
            help="Disabled: Upload documents first" if is_disabled else "Show retrieved documents",
            disabled=is_disabled
        )
    else:
        top_k = 0
        use_agent = False  # Agent not applicable for direct LLM queries
        show_details = False

clear_col, _ = st.columns([1, 1])

with clear_col:
    # Disable Clear button when in RAG mode with no documents
    clear_button_disabled = show_upload and not has_documents
    clear_clicked = st.button(
        "🧹 Clear", 
        use_container_width=True,
        disabled=clear_button_disabled,
        help="Upload documents first to enable RAG queries" if clear_button_disabled else None
    )

# Handle clear button - clears immediately and forces widget refresh
if clear_clicked:
    st.session_state["query_input"] = ""
    st.session_state["chat_history"] = []
    st.session_state["widget_refresh_counter"] += 1  # Force widget recreation
    st.rerun()

# Process query
if ask_clicked:
    if not query_text.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        with st.spinner("🤔 Thinking..."):
            try:
                query = query_text.strip()
                contextual_query = build_contextual_query(query)
                st.session_state["chat_history"].append({
                    "role": "user",
                    "content": query
                })
                retrieved_docs = []
                
                # Determine if we need RAG
                if show_upload and has_documents:
                    rag_system_prompt = build_rag_system_prompt()

                    # RAG Query
                    if use_agent:
                        # Use agent for complex queries (handles retrieval internally)
                        agent = AIAgent(pipeline)
                        result = agent.process_query(query, top_k=top_k, system_prompt=rag_system_prompt)
                        response = result.get('response', '')
                        retrieved_docs = result.get('retrieved_docs', [])
                    else:
                        # Standard RAG response
                        retrieved_docs = pipeline.retrieve(query, top_k=top_k)
                        response = pipeline.generate_response(query, retrieved_docs, system_prompt=rag_system_prompt)
                
                else:
                    # Direct LLM Query (no RAG)
                    if use_agent:
                        agent = AIAgent(pipeline)
                        result = agent.process_query(contextual_query, top_k=0)
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
                            pipeline.HumanMessage(content=contextual_query)
                        ]
                        response = pipeline.llm.invoke(messages).content

                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": response,
                    "retrieved_docs": retrieved_docs,
                    "show_details": show_details if show_upload else False
                })

                st.session_state["query_input"] = ""
                st.session_state["widget_refresh_counter"] += 1
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": f"❌ Error: {str(e)}"
                })
                logger.error(f"Query error: {str(e)}")

# Footer
st.divider()
st.caption("🚀 Standalone AI Agent RAG System - Powered by Groq AI")
