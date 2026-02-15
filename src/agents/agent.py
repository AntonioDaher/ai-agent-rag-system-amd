"""Agent-based reasoning and planning"""
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from src.config.logger import setup_logger
from src.config.settings import settings
from src.rag.pipeline import RAGPipeline

logger = setup_logger(__name__)


class AgentAction(str, Enum):
    """Agent action types"""
    PLAN = "plan"
    RETRIEVE = "retrieve"
    REASON = "reason"
    GENERATE = "generate"
    VALIDATE = "validate"


@dataclass
class AgentThought:
    """Represents an agent's thought or action"""
    action: AgentAction
    description: str
    input: Optional[Dict] = None
    output: Optional[Dict] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class DocumentRetrievalAgent:
    """Agent responsible for document retrieval"""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """Initialize retrieval agent"""
        self.name = "DocumentRetrievalAgent"
        self.rag_pipeline = rag_pipeline
    
    def execute(self, query: str, top_k: int = 5) -> Dict:
        """Retrieve relevant documents"""
        logger.info(f"[{self.name}] Retrieving documents for: {query}")
        
        try:
            retrieved_docs = self.rag_pipeline.retrieve(query, top_k)
            
            return {
                "status": "success",
                "agent": self.name,
                "retrieved_docs": retrieved_docs,
                "doc_count": len(retrieved_docs)
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }


class ReasoningAgent:
    """Agent responsible for reasoning and analysis"""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """Initialize reasoning agent"""
        self.name = "ReasoningAgent"
        self.rag_pipeline = rag_pipeline
    
    def analyze_documents(self, docs: List[Dict]) -> Dict:
        """Analyze retrieved documents"""
        logger.info(f"[{self.name}] Analyzing {len(docs)} documents")
        
        analysis = {
            "total_docs": len(docs),
            "documents": [],
            "key_insights": []
        }
        
        for doc in docs:
            analysis["documents"].append({
                "source": doc.get("source_file"),
                "similarity": doc.get("similarity"),
                "chunk_index": doc.get("chunk_index")
            })
        
        return analysis
    
    def execute(self, query: str, retrieved_docs: List[Dict]) -> Dict:
        """Execute reasoning"""
        logger.info(f"[{self.name}] Reasoning about: {query}")
        
        try:
            analysis = self.analyze_documents(retrieved_docs)
            
            return {
                "status": "success",
                "agent": self.name,
                "analysis": analysis,
                "reasoning": f"Analyzed {len(retrieved_docs)} documents for relevance to query"
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }


class ResponseGenerationAgent:
    """Agent responsible for generating final responses"""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """Initialize generation agent"""
        self.name = "ResponseGenerationAgent"
        self.rag_pipeline = rag_pipeline
    
    def execute(self, query: str, retrieved_docs: List[Dict], system_prompt: Optional[str] = None) -> Dict:
        """Generate response"""
        logger.info(f"[{self.name}] Generating response for: {query}")
        
        try:
            response = self.rag_pipeline.generate_response(query, retrieved_docs, system_prompt)
            
            return {
                "status": "success",
                "agent": self.name,
                "response": response
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }


class ValidationAgent:
    """Agent responsible for validating outputs"""
    
    def __init__(self):
        """Initialize validation agent"""
        self.name = "ValidationAgent"
    
    def validate_response(self, response: str, query: str) -> Dict:
        """Validate response quality"""
        logger.info(f"[{self.name}] Validating response")
        
        validation_result = {
            "is_valid": True,
            "checks": {}
        }
        
        # Check 1: Response is not empty
        validation_result["checks"]["non_empty"] = len(response.strip()) > 0
        
        # Check 2: Response is relevant length
        validation_result["checks"]["adequate_length"] = len(response.split()) >= 10
        
        # Check 3: Response contains relevant keywords from query
        query_keywords = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_keywords.intersection(response_words))
        validation_result["checks"]["keyword_relevance"] = overlap >= max(1, len(query_keywords) // 2)
        
        # Overall validity
        validation_result["is_valid"] = all(validation_result["checks"].values())
        
        return validation_result
    
    def execute(self, response: str, query: str, retrieved_docs: List[Dict]) -> Dict:
        """Execute validation"""
        try:
            validation = self.validate_response(response, query)
            
            return {
                "status": "success",
                "agent": self.name,
                "validation": validation,
                "is_valid": validation["is_valid"]
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }


class AIAgent:
    """Main orchestrator agent that coordinates all sub-agents"""
    
    def __init__(self, rag_pipeline: RAGPipeline):
        """Initialize AI Agent"""
        self.name = "AIAgent"
        self.rag_pipeline = rag_pipeline
        
        # Initialize sub-agents
        self.retrieval_agent = DocumentRetrievalAgent(rag_pipeline)
        self.reasoning_agent = ReasoningAgent(rag_pipeline)
        self.generation_agent = ResponseGenerationAgent(rag_pipeline)
        self.validation_agent = ValidationAgent()
        
        self.thoughts: List[AgentThought] = []
    
    def think(self, action: AgentAction, description: str, input_data: Optional[Dict] = None) -> AgentThought:
        """Record agent thought"""
        thought = AgentThought(
            action=action,
            description=description,
            input=input_data
        )
        self.thoughts.append(thought)
        logger.info(f"[{self.name}] Thought: {action.value} - {description}")
        return thought
    
    def process_query(
        self,
        query: str,
        top_k: int = 5,
        system_prompt: Optional[str] = None,
        return_thoughts: bool = True
    ) -> Dict:
        """Process a query using coordinated agents"""
        logger.info(f"[{self.name}] Processing query: {query}")
        self.thoughts = []  # Reset thoughts
        
        # Step 1: Plan
        self.think(AgentAction.PLAN, "Analyzing query and planning retrieval strategy")
        
        # Step 2: Retrieve
        self.think(AgentAction.RETRIEVE, f"Retrieving top {top_k} relevant documents")
        retrieval_result = self.retrieval_agent.execute(query, top_k)
        
        if retrieval_result["status"] != "success":
            return {
                "status": "error",
                "error": retrieval_result.get("error"),
                "thoughts": [vars(t) for t in self.thoughts] if return_thoughts else None
            }
        
        retrieved_docs = retrieval_result["retrieved_docs"]
        
        # Step 3: Reason
        self.think(AgentAction.REASON, "Analyzing retrieved documents for relevance and consistency")
        reasoning_result = self.reasoning_agent.execute(query, retrieved_docs)
        
        # Step 4: Generate
        self.think(AgentAction.GENERATE, "Generating comprehensive response based on analysis")
        generation_result = self.generation_agent.execute(query, retrieved_docs, system_prompt)
        
        if generation_result["status"] != "success":
            return {
                "status": "error",
                "error": generation_result.get("error"),
                "thoughts": [vars(t) for t in self.thoughts] if return_thoughts else None
            }
        
        response = generation_result["response"]
        
        # Step 5: Validate
        self.think(AgentAction.VALIDATE, "Validating response quality and relevance")
        validation_result = self.validation_agent.execute(response, query, retrieved_docs)
        
        # Compile final result
        result = {
            "status": "success",
            "query": query,
            "response": response,
            "retrieved_docs": retrieved_docs,
            "reasoning": reasoning_result.get("reasoning"),
            "validation": validation_result.get("validation"),
            "is_valid_response": validation_result.get("is_valid", True)
        }
        
        if return_thoughts:
            result["thoughts"] = [vars(t) for t in self.thoughts]
            result["thought_count"] = len(self.thoughts)
        
        logger.info(f"[{self.name}] Query processed successfully")
        return result
    
    def get_thought_history(self) -> List[Dict]:
        """Get agent thought history"""
        return [vars(t) for t in self.thoughts]
