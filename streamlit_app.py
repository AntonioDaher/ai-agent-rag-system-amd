import os
import json
import requests
import streamlit as st

DEFAULT_API_URL = os.getenv("RAG_API_URL", "https://ai-agent-rag-api.onrender.com")
DEFAULT_API_KEY = os.getenv("RAG_API_KEY", "")


def build_headers(api_key: str) -> dict:
    if not api_key:
        return {}
    return {"Authorization": f"Bearer {api_key}"}

st.set_page_config(
    page_title="AI Agent RAG System",
    page_icon="📄",
    layout="wide",
)

st.title("AI Agent RAG System")
st.caption("Query the LLM directly or Upload Docs / Files to use the RAG API.")

with st.sidebar:
    st.header("Server Settings")
    api_url = st.text_input("API Base URL", value=DEFAULT_API_URL)
    api_key = st.text_input("API Key (optional)", value=DEFAULT_API_KEY, type="password")
    st.caption("Example: https://your-domain.com or http://127.0.0.1:9011")
    if st.button("Check Health"):
        try:
            resp = requests.get(f"{api_url}/health", timeout=10)
            if resp.ok:
                st.success("Server is reachable.")
                st.json(resp.json())
            else:
                st.error(f"Server error: {resp.status_code}")
        except Exception as exc:
            st.error(f"Health check failed: {exc}")

st.subheader("1) Query Mode Options")
query_mode = st.radio(
    "How do you want to query?",
    options=[
        "LLM Direct Query (No Uploads)",
        "RAG Query (Upload Documents / Files)",
    ],
    index=0,
    horizontal=True,
)

show_upload = query_mode == "RAG Query (Upload Documents / Files)"
if show_upload:
    st.subheader("2) Upload a document")

    upload_col, info_col = st.columns([2, 3])
    with upload_col:
        upload_files = st.file_uploader(
            "Choose document(s)",
            type=["pdf", "txt", "csv", "xlsx", "docx"],
            accept_multiple_files=True,
            key="file_uploader",
        )
        button_col1, button_col2 = st.columns(2)
        with button_col1:
            upload_clicked = st.button("Upload", use_container_width=True)
        with button_col2:
            reset_clicked = st.button("Reset Store", type="secondary", use_container_width=True)

    with info_col:
        st.markdown(
            """
**Upload**: Add documents to the vector store. Files are chunked and indexed for querying.

**Reset Store**: ⚠️ Complete reset - deletes both the vector store index AND all uploaded files. This action requires confirmation.
            """
        )

    if upload_clicked:
        if not upload_files:
            st.warning("Please select one or more files to upload.")
        else:
            headers = build_headers(api_key)
            for up in upload_files:
                try:
                    files = {"file": (up.name, up.getvalue())}
                    resp = requests.post(
                        f"{api_url}/upload",
                        files=files,
                        headers=headers,
                        timeout=120,
                    )
                    if resp.ok:
                        st.success(f"Uploaded: {up.name}")
                        st.json(resp.json())
                    else:
                        st.error(f"Upload failed ({up.name}): {resp.status_code}")
                        st.text(resp.text)
                except Exception as exc:
                    st.error(f"Upload error ({up.name}): {exc}")

    # Initialize reset confirmation state
    if "reset_confirmation" not in st.session_state:
        st.session_state["reset_confirmation"] = False
    
    # Initialize store_empty flag
    if "store_empty" not in st.session_state:
        st.session_state["store_empty"] = False

    if reset_clicked:
        st.session_state["reset_confirmation"] = True

    if st.session_state["reset_confirmation"]:
        st.warning("⚠️ This will delete ALL uploaded documents from the vector store!")
        confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 2])
        with confirm_col1:
            if st.button("Confirm Reset", type="primary"):
                try:
                    headers = build_headers(api_key)
                    resp = requests.delete(
                        f"{api_url}/vector-store/reset",
                        headers=headers,
                        timeout=30,
                    )
                    if resp.ok:
                        st.success("✅ Vector store reset successfully!")
                        st.json(resp.json())
                        # Clear the file uploader widget
                        if "file_uploader" in st.session_state:
                            del st.session_state["file_uploader"]
                        # Reset confirmation state
                        st.session_state["reset_confirmation"] = False
                        # Mark store as empty
                        st.session_state["store_empty"] = True
                        st.rerun()
                    else:
                        st.error(f"Reset failed: {resp.status_code}")
                        st.text(resp.text)
                except Exception as exc:
                    st.error(f"Reset error: {exc}")
        with confirm_col2:
            if st.button("Cancel"):
                st.session_state["reset_confirmation"] = False
                st.rerun()
    
    # Show notification banner if store is empty
    if st.session_state.get("store_empty", False):
        st.info("📁 The document store is empty. Please upload documents before querying.")
    
    st.divider()
else:
    st.divider()

# Check if there are documents in the store (for RAG mode)
has_documents = False
if show_upload:
    if upload_files:
        has_documents = True
        st.session_state["store_empty"] = False
    else:
        try:
            headers = build_headers(api_key)
            resp = requests.get(f"{api_url}/vector-store/stats", headers=headers, timeout=10)
            if resp.ok:
                stats = resp.json()
                has_documents = stats.get("total_chunks", 0) > 0
                if has_documents:
                    st.session_state["store_empty"] = False
        except:
            pass

query_step = 3 if show_upload else 2
st.subheader(f"{query_step}) Your Query")
if query_mode == "LLM Direct Query (No Uploads)":
    st.info("This mode skips document retrieval and answers directly from the LLM.")

# Check if query should be disabled in RAG mode
query_disabled = False
if query_mode == "RAG Query (Upload Documents / Files)":
    if not has_documents:
        query_disabled = True

query_col, options_col = st.columns([3, 1])
with query_col:
    def _clear_query() -> None:
        st.session_state["query_text"] = ""

    if query_mode == "LLM Direct Query (No Uploads)":
        placeholder_text = "Ask anything for a direct LLM response..."
    elif query_mode == "RAG Query (Upload Documents / Files)":
        if query_disabled:
            placeholder_text = "⚠️ Please upload documents first before querying..."
        else:
            placeholder_text = "Ask about the document(s) you just uploaded..."

    query_text = st.text_area(
        "Post your question below",
        placeholder=placeholder_text,
        height=120,
        key="query_text",
        disabled=query_disabled,
    )
with options_col:
    if query_mode != "LLM Direct Query (No Uploads)":
        top_k = st.slider("Top K", min_value=1, max_value=10, value=3)
    else:
        top_k = 0
    use_agent = st.checkbox("Use Agent", value=False)
    show_details = st.checkbox("Show details", value=False)

ask_col, clear_col = st.columns([1, 1])
with ask_col:
    ask_clicked = st.button("Ask")
with clear_col:
    st.button("Clear", on_click=_clear_query)

if ask_clicked:
    if not query_text.strip():
        st.warning("Please enter a question.")
    else:
        try:
            effective_top_k = 0 if query_mode == "LLM Direct Query (No Uploads)" else top_k
            payload = {
                "query": query_text.strip(),
                "top_k": effective_top_k,
                "use_agent": use_agent,
            }
            headers = build_headers(api_key)
            resp = requests.post(
                f"{api_url}/query",
                json=payload,
                headers=headers,
                timeout=120,
            )
            if resp.ok:
                data = resp.json()
                st.success("Answer received.")
                st.markdown("**Answer**")
                st.write(data.get("response", ""))

                if show_details:
                    retrieved = data.get("retrieved_docs", [])
                    st.markdown("**Retrieved Documents**")
                    if not retrieved:
                        st.info("No documents retrieved.")
                    else:
                        for i, doc in enumerate(retrieved, 1):
                            title = f"Document {i}: {doc.get('source_file', 'unknown')} (sim={doc.get('similarity', 0):.3f})"
                            with st.expander(title):
                                content = doc.get("content", "")
                                if content:
                                    st.text(content)
                                else:
                                    st.caption("No content available for this chunk.")

                    st.markdown("**Raw Response**")
                    st.json(data)
            else:
                st.error(f"Query failed: {resp.status_code}")
                st.text(resp.text)
        except Exception as exc:
            st.error(f"Query error: {exc}")

st.divider()

st.caption(
    "Tip: For public sharing, deploy the FastAPI server and set RAG_API_URL to the public endpoint."
)
