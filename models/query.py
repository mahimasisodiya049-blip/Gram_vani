"""Query-related data models."""

from dataclasses import dataclass
from typing import List
from .document import TextChunk


@dataclass
class QueryResult:
    """Result of a query operation."""
    
    query_id: str
    query_text: str
    answer_text: str
    answer_audio: bytes
    language: str
    retrieved_chunks: List[TextChunk]
    processing_time_ms: int
    
    def validate(self) -> tuple[bool, str | None]:
        """Validate query result.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.query_id or not self.query_id.strip():
            return False, "query_id cannot be empty"
        
        if not self.query_text or not self.query_text.strip():
            return False, "query_text cannot be empty"
        
        if not self.answer_text or not self.answer_text.strip():
            return False, "answer_text cannot be empty"
        
        if not self.answer_audio or len(self.answer_audio) == 0:
            return False, "answer_audio cannot be empty"
        
        if not self.language or not self.language.strip():
            return False, "language cannot be empty"
        
        if self.processing_time_ms < 0:
            return False, "processing_time_ms cannot be negative"
        
        return True, None
