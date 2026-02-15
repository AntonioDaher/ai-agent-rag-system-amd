"""Retrieval-Augmented Generation (RAG) pipeline"""
from typing import List, Dict, Optional
from src.config.logger import setup_logger
from src.config.settings import settings
from src.embeddings.embedding import EmbeddingManager
from src.retrieval.vector_store import VectorStoreManager

logger = setup_logger(__name__)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline"""
    
    def __init__(self, use_openai_embeddings: bool = False):
        """Initialize RAG pipeline"""
        self.embedding_manager = EmbeddingManager(use_openai=use_openai_embeddings)
        self.vector_store_manager = VectorStoreManager(
            dimension=self.embedding_manager.get_dimension()
        )
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM client"""
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            
            self.ChatOpenAI = ChatOpenAI
            self.SystemMessage = SystemMessage
            self.HumanMessage = HumanMessage
            
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
                openai_api_key=settings.openai_api_key,
            )
            logger.info(f"Initialized LLM: {settings.llm_model}")
        except ImportError:
            logger.error("langchain and openai packages are required")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve relevant documents for a query"""
        # Generate embedding for query
        query_embedding = self.embedding_manager.embed_text(query)
        
        # Search vector store
        results = self.vector_store_manager.search(query_embedding, top_k)
        
        logger.info(f"Retrieved {len(results)} documents for query")
        return results
    
    def generate_response(
        self,
        query: str,
        retrieved_docs: List[Dict],
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate response using LLM with retrieved context"""
        # Build context from retrieved documents
        context = "\n\n".join([
            f"Document: {doc['source_file']} (Chunk {doc['chunk_index']}/{doc['total_chunks']})\n"
            f"Content: {doc.get('content', 'No content')}"
            for doc in retrieved_docs
        ])
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are an intelligent assistant that answers questions based on provided documents.
            
            Guidelines:
            - Answer questions using only the information from the provided documents
            - Be clear and concise in your responses
            - If the information is not in the documents, clearly state that
            - Cite the document and chunk number when relevant"""
        
        # Build user message
        user_message = f"""Based on the following documents, please answer the question:

DOCUMENTS:
{context}

QUESTION: {query}

ANSWER:"""
        
        try:
            # Call LLM
            messages = [
                self.SystemMessage(content=system_prompt),
                self.HumanMessage(content=user_message)
            ]
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def query(self, query: str, top_k: int = 5, system_prompt: Optional[str] = None) -> Dict:
        """Complete RAG query: retrieve and generate response"""
        try:
            # Step 1: Retrieve
            retrieved_docs = self.retrieve(query, top_k)
            
            # Step 2: Generate
            response = self.generate_response(query, retrieved_docs, system_prompt)
            
            return {
                "query": query,
                "response": response,
                "retrieved_docs": retrieved_docs,
                "doc_count": len(retrieved_docs)
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {str(e)}")
            raise
    
    def get_vector_store_stats(self) -> Dict:
        """Get vector store statistics"""
        return self.vector_store_manager.get_statistics()
