"""Document-related data models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class DocumentMetadata:
    """Metadata for uploaded documents."""
    
    document_id: str
    user_id: str
    filename: str
    s3_key: str
    upload_timestamp: datetime
    processing_status: str  # pending, processing, completed, failed
    num_pages: int
    num_chunks: int
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate document metadata.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.document_id or not self.document_id.strip():
            return False, "document_id cannot be empty"
        
        if not self.user_id or not self.user_id.strip():
            return False, "user_id cannot be empty"
        
        if not self.filename or not self.filename.strip():
            return False, "filename cannot be empty"
        
        if not self.s3_key or not self.s3_key.strip():
            return False, "s3_key cannot be empty"
        
        valid_statuses = {"pending", "processing", "completed", "failed"}
        if self.processing_status not in valid_statuses:
            return False, f"processing_status must be one of {valid_statuses}"
        
        if self.num_pages < 0:
            return False, "num_pages cannot be negative"
        
        if self.num_chunks < 0:
            return False, "num_chunks cannot be negative"
        
        return True, None


@dataclass
class TextChunk:
    """Represents a chunk of text from a document."""
    
    chunk_id: str
    document_id: str
    text: str
    page_number: int
    chunk_index: int
    embedding: Optional[List[float]] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate text chunk.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.chunk_id or not self.chunk_id.strip():
            return False, "chunk_id cannot be empty"
        
        if not self.document_id or not self.document_id.strip():
            return False, "document_id cannot be empty"
        
        if not self.text or not self.text.strip():
            return False, "text cannot be empty"
        
        if self.page_number < 0:
            return False, "page_number cannot be negative"
        
        if self.chunk_index < 0:
            return False, "chunk_index cannot be negative"
        
        if self.embedding is not None and len(self.embedding) == 0:
            return False, "embedding cannot be empty list"
        
        return True, None
