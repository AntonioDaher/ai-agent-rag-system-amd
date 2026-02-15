"""Safety and reliability controls"""
import re
from typing import Dict, List, Tuple, Optional
from src.config.logger import setup_logger

logger = setup_logger(__name__)


class InputValidator:
    """Validate user inputs"""
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r"SELECT.*FROM",  # SQL injection
        r"<script.*?>",    # Script injection
        r"javascript:",    # JavaScript injection
        r"\${.*}",         # Template injection
    ]
    
    # Maximum lengths
    MAX_QUERY_LENGTH = 5000
    MIN_QUERY_LENGTH = 3
    
    @staticmethod
    def validate_query(query: str) -> Tuple[bool, Optional[str]]:
        """Validate query input"""
        if not query:
            return False, "Query cannot be empty"
        
        if len(query) < InputValidator.MIN_QUERY_LENGTH:
            return False, f"Query must be at least {InputValidator.MIN_QUERY_LENGTH} characters"
        
        if len(query) > InputValidator.MAX_QUERY_LENGTH:
            return False, f"Query exceeds maximum length of {InputValidator.MAX_QUERY_LENGTH} characters"
        
        # Check for suspicious patterns (case-insensitive)
        query_upper = query.upper()
        for pattern in InputValidator.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return False, "Query contains suspicious patterns"
        
        return True, None
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: List[str]) -> Tuple[bool, Optional[str]]:
        """Validate file path"""
        if not file_path:
            return False, "File path cannot be empty"
        
        # Extract extension
        extension = file_path.split('.')[-1].lower()
        
        if extension not in allowed_extensions:
            return False, f"File type .{extension} not allowed. Allowed: {', '.join(allowed_extensions)}"
        
        return True, None


class HallucinationDetector:
    """Detect potential hallucinations in responses"""
    
    @staticmethod
    def detect_unsupported_claims(response: str, retrieved_docs: List[Dict]) -> Dict:
        """Detect claims not supported by retrieved documents"""
        
        # Extract key phrases from response (simplified)
        response_sentences = response.split('.')
        
        # Extract text from documents
        doc_texts = []
        for doc in retrieved_docs:
            if 'content' in doc:
                doc_texts.append(doc['content'].lower())
        
        combined_doc_text = " ".join(doc_texts).lower()
        
        unsupported_sentences = []
        
        for sentence in response_sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Check if key words from sentence appear in documents
            words = sentence.lower().split()
            meaningful_words = [w for w in words if len(w) > 4]
            
            if meaningful_words:
                overlap = sum(1 for w in meaningful_words if w in combined_doc_text)
                
                # If less than 30% of meaningful words are in documents, flag as potential hallucination
                if overlap / len(meaningful_words) < 0.3:
                    unsupported_sentences.append(sentence)
        
        return {
            "has_potential_hallucinations": len(unsupported_sentences) > 0,
            "unsupported_sentences_count": len(unsupported_sentences),
            "unsupported_sentences": unsupported_sentences[:5]  # Top 5
        }
    
    @staticmethod
    def check_citations(response: str, retrieved_docs: List[Dict]) -> Dict:
        """Check if response properly cites sources"""
        
        citation_patterns = [
            r"\(.*?source.*?\)",
            r"\[.*?\d+.*?\]",
            r"according to.*?:",
            r"as mentioned in"
        ]
        
        has_citations = False
        for pattern in citation_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                has_citations = True
                break
        
        return {
            "has_citations": has_citations,
            "recommendation": "Add source citations for credibility" if not has_citations else "Response includes citations"
        }


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter"""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = {}
    
    def is_allowed(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check if request is allowed"""
        import time
        
        current_time = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove old requests outside the window
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if current_time - req_time < self.window_seconds
        ]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return False, f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds"
        
        self.requests[user_id].append(current_time)
        return True, None


class ErrorHandler:
    """Centralized error handling"""
    
    @staticmethod
    def handle_exception(exception: Exception, context: str = "") -> Dict:
        """Handle exceptions gracefully"""
        logger.error(f"Error in {context}: {str(exception)}")
        
        # Map common exceptions to user-friendly messages
        error_messages = {
            "KeyError": "Data retrieval error occurred",
            "ValueError": "Invalid value provided",
            "TimeoutError": "Request timeout - please try again",
            "ConnectionError": "Connection error - please check your network",
            "ImportError": "Required dependency not available",
        }
        
        exception_type = type(exception).__name__
        user_message = error_messages.get(exception_type, "An unexpected error occurred")
        
        return {
            "status": "error",
            "message": user_message,
            "details": str(exception),
            "type": exception_type,
            "context": context
        }
    
    @staticmethod
    def validate_response_before_return(response: Dict) -> Dict:
        """Validate response before returning to user"""
        
        required_fields = ["status"]
        for field in required_fields:
            if field not in response:
                response[field] = "error"
        
        # Sanitize error messages
        if "error" in response and response["error"]:
            # Don't expose internal system details
            if "traceback" in str(response["error"]).lower():
                response["error"] = "An internal error occurred"
        
        return response


class SafetyManager:
    """Centralized safety management"""
    
    def __init__(self):
        """Initialize safety manager"""
        self.input_validator = InputValidator()
        self.hallucination_detector = HallucinationDetector()
        self.rate_limiter = RateLimiter()
        self.error_handler = ErrorHandler()
    
    def validate_and_sanitize_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate and sanitize query"""
        return self.input_validator.validate_query(query)
    
    def check_response_quality(self, response: str, retrieved_docs: List[Dict]) -> Dict:
        """Check response quality"""
        hallucination_check = self.hallucination_detector.detect_unsupported_claims(response, retrieved_docs)
        citation_check = self.hallucination_detector.check_citations(response, retrieved_docs)
        
        return {
            "hallucination_check": hallucination_check,
            "citation_check": citation_check,
            "overall_quality": {
                "is_safe": not hallucination_check["has_potential_hallucinations"],
                "needs_citations": not citation_check["has_citations"]
            }
        }
    
    def check_rate_limit(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check rate limit for user"""
        return self.rate_limiter.is_allowed(user_id)
