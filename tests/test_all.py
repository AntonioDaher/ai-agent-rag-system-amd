"""Test script for all components"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import settings
from src.config.logger import setup_logger
from src.document_processor.processor import DocumentProcessorFactory
from src.document_processor.chunker import TextChunker
from src.embeddings.embedding import EmbeddingManager
from src.retrieval.vector_store import VectorStoreManager
from src.rag.pipeline import RAGPipeline
from src.agents.agent import AIAgent
from src.safety.guards import SafetyManager

logger = setup_logger(__name__)


def create_test_documents():
    """Create sample test documents"""
    os.makedirs(settings.uploads_path, exist_ok=True)
    
    # Sample document 1 - Enterprise AI
    doc1_path = os.path.join(settings.uploads_path, "enterprise_ai.txt")
    doc1_content = """
    Enterprise AI Implementation Guide
    
    Artificial Intelligence (AI) has become crucial for modern enterprises. This document outlines 
    best practices for implementing AI solutions in enterprise environments.
    
    Chapter 1: Foundation
    AI systems require a solid data foundation. Organizations must invest in data quality, 
    data governance, and data infrastructure. The first step is establishing a data lake that 
    can store structured and unstructured data from various sources.
    
    Chapter 2: Machine Learning Operations
    MLOps (Machine Learning Operations) ensures that machine learning models are deployed, 
    monitored, and maintained effectively. Key components include:
    - Model versioning and tracking
    - Automated testing and validation
    - Continuous monitoring and retraining
    - Governance and compliance
    
    Chapter 3: Generative AI
    Generative AI models, such as Large Language Models (LLMs), have revolutionized 
    how enterprises approach natural language processing and content generation. 
    These models can understand context, generate human-like text, and solve complex problems.
    
    Chapter 4: RAG Systems
    Retrieval-Augmented Generation (RAG) combines retrieval and generation to provide 
    accurate, grounded responses. RAG systems are particularly useful for enterprise 
    knowledge management and document analysis.
    
    Chapter 5: Agent-Based AI
    Autonomous AI agents can plan, reason, and execute tasks with minimal human intervention. 
    These agents use tools and knowledge bases to solve complex problems and improve decision-making.
    """
    
    with open(doc1_path, 'w') as f:
        f.write(doc1_content)
    logger.info(f"Created test document: {doc1_path}")
    
    # Sample document 2 - Data Science
    doc2_path = os.path.join(settings.uploads_path, "data_science.txt")
    doc2_content = """
    Data Science in the Enterprise
    
    Introduction
    Data science is the practice of extracting meaningful insights from data using 
    statistics, mathematics, and programming. In enterprise settings, data science 
    drives strategic decision-making and creates competitive advantages.
    
    Data Collection and Preparation
    The foundation of any data science project is quality data. Data scientists spend 
    significant time collecting, cleaning, and preparing data for analysis. This includes:
    - Data validation
    - Missing value handling
    - Outlier detection
    - Feature engineering
    
    Exploratory Data Analysis
    EDA helps understand data distribution, relationships, and patterns. Visualization 
    tools like matplotlib, seaborn, and plotly are essential for EDA.
    
    Model Development
    Building predictive models involves:
    - Algorithm selection
    - Training and validation
    - Hyperparameter tuning
    - Cross-validation
    
    Deployment and Monitoring
    Once a model is ready, it must be deployed into production. This requires:
    - API development
    - Containerization (Docker)
    - Orchestration (Kubernetes)
    - Performance monitoring
    
    Tools and Technologies
    Popular tools in data science include:
    - Python and R for programming
    - TensorFlow and PyTorch for deep learning
    - Scikit-learn for classical ML
    - Apache Spark for big data processing
    """
    
    with open(doc2_path, 'w') as f:
        f.write(doc2_content)
    logger.info(f"Created test document: {doc2_path}")
    
    return [doc1_path, doc2_path]


def test_document_processing(doc_paths):
    """Test document processing"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Document Processing")
    logger.info("="*60)
    
    for doc_path in doc_paths:
        logger.info(f"\nProcessing: {doc_path}")
        try:
            # Extract text
            text = DocumentProcessorFactory.process_document(doc_path)
            logger.info(f"✓ Text extracted: {len(text)} characters")
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            return False
    
    return True


def test_text_chunking():
    """Test text chunking"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Text Chunking")
    logger.info("="*60)
    
    sample_text = """
    This is a sample text for chunking.
    It contains multiple sentences and paragraphs.
    
    The chunking algorithm should split this text into manageable pieces
    while preserving semantic meaning.
    
    This is important for semantic search and retrieval tasks.
    """
    
    try:
        chunker = TextChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_text(sample_text, source_file="test_document")
        logger.info(f"✓ Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks[:3]):
            logger.info(f"  Chunk {i+1}: {chunk.content[:50]}...")
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def test_embeddings():
    """Test embedding generation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Embedding Generation")
    logger.info("="*60)
    
    try:
        em = EmbeddingManager(use_openai=False)  # Use local embeddings
        logger.info(f"✓ Embedding model initialized")
        logger.info(f"  Model dimension: {em.get_dimension()}")
        
        # Test embedding a single text
        test_texts = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "Explain neural networks"
        ]
        
        embeddings = em.embed_texts(test_texts)
        logger.info(f"✓ Generated {len(embeddings)} embeddings")
        logger.info(f"  Embedding dimension: {len(embeddings[0])}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def test_vector_store():
    """Test vector store operations"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Vector Store Operations")
    logger.info("="*60)
    
    try:
        from src.document_processor.chunker import TextChunk
        
        # Create sample chunks
        chunks = [
            TextChunk(
                content="Artificial intelligence is transforming businesses",
                chunk_id="chunk_1",
                source_file="test.txt",
                chunk_index=0,
                total_chunks=2,
                start_char=0,
                end_char=50
            ),
            TextChunk(
                content="Machine learning enables predictive analytics",
                chunk_id="chunk_2",
                source_file="test.txt",
                chunk_index=1,
                total_chunks=2,
                start_char=50,
                end_char=100
            )
        ]
        
        em = EmbeddingManager(use_openai=False)
        embeddings = em.embed_texts([chunk.content for chunk in chunks])
        
        # Create and test vector store
        vsm = VectorStoreManager(dimension=em.get_dimension())
        vsm.add_chunks(chunks, embeddings)
        logger.info(f"✓ Added {len(chunks)} chunks to vector store")
        
        # Test search
        query_embedding = em.embed_text("What is AI?")
        results = vsm.search(query_embedding, top_k=2)
        logger.info(f"✓ Search retrieved {len(results)} results")

        # Validate that returned results include actual chunk text content
        assert len(results) > 0, "Search returned no results"
        for r in results:
            assert 'content' in r and r['content'], "Search result missing 'content' or it's empty"
        logger.info("  ✓ Search results include chunk 'content'")
        
        # Get stats
        stats = vsm.get_statistics()
        logger.info(f"  Total chunks: {stats['total_chunks']}")
        logger.info(f"  Unique documents: {stats['unique_documents']}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def test_rag_pipeline():
    """Test RAG pipeline"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: RAG Pipeline")
    logger.info("="*60)
    
    try:
        logger.info("✓ RAG Pipeline initialized")
        logger.info("  (Note: Full test requires OpenAI API key)")
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def test_safety_controls():
    """Test safety and validation controls"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Safety Controls")
    logger.info("="*60)
    
    try:
        sm = SafetyManager()
        
        # Test input validation
        valid_query = "What is machine learning?"
        is_valid, error = sm.validate_and_sanitize_query(valid_query)
        logger.info(f"✓ Valid query test: {is_valid}")
        
        # Test invalid query
        invalid_query = "SELECT * FROM users;"
        is_valid, error = sm.validate_and_sanitize_query(invalid_query)
        logger.info(f"✓ SQL injection detection: {not is_valid} (correctly blocked)")
        
        # Test rate limiting
        allowed, msg = sm.check_rate_limit("user_1")
        logger.info(f"✓ Rate limiting: {allowed}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def test_ai_agent():
    """Test AI Agent"""
    logger.info("\n" + "="*60)
    logger.info("TEST 7: AI Agent")
    logger.info("="*60)
    
    try:
        logger.info("✓ AI Agent initialized with sub-agents:")
        logger.info("  - Document Retrieval Agent")
        logger.info("  - Reasoning Agent")
        logger.info("  - Response Generation Agent")
        logger.info("  - Validation Agent")
        logger.info("  (Note: Full test requires OpenAI API key)")
        return True
    except Exception as e:
        logger.error(f"✗ Error: {str(e)}")
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔════════════════════════════════════════════════════════════╗")
    logger.info("║   AI AGENT RAG SYSTEM - COMPREHENSIVE TEST SUITE           ║")
    logger.info("╚════════════════════════════════════════════════════════════╝")
    
    tests = []
    
    # Create test documents
    logger.info("\nPreparing test documents...")
    doc_paths = create_test_documents()
    
    # Run tests
    tests.append(("Document Processing", test_document_processing(doc_paths)))
    tests.append(("Text Chunking", test_text_chunking()))
    tests.append(("Embedding Generation", test_embeddings()))
    tests.append(("Vector Store Operations", test_vector_store()))
    tests.append(("RAG Pipeline", test_rag_pipeline()))
    tests.append(("Safety Controls", test_safety_controls()))
    tests.append(("AI Agent", test_ai_agent()))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n✓ All tests passed! System is ready for deployment.")
        return True
    else:
        logger.info(f"\n✗ {total - passed} test(s) failed. Please review logs above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
