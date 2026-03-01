"""API response data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class UploadResult:
    """Result of a document upload operation."""
    
    upload_id: str
    status: str  # success, failed
    message: str
    document_id: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate upload result.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.upload_id or not self.upload_id.strip():
            return False, "upload_id cannot be empty"
        
        valid_statuses = {"success", "failed"}
        if self.status not in valid_statuses:
            return False, f"status must be one of {valid_statuses}"
        
        if not self.message or not self.message.strip():
            return False, "message cannot be empty"
        
        if self.status == "success" and not self.document_id:
            return False, "document_id is required when status is success"
        
        return True, None


@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription."""
    
    text: str
    language: str
    confidence: float
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate transcription result.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.text or not self.text.strip():
            return False, "text cannot be empty"
        
        if not self.language or not self.language.strip():
            return False, "language cannot be empty"
        
        if not 0.0 <= self.confidence <= 1.0:
            return False, "confidence must be between 0.0 and 1.0"
        
        return True, None


@dataclass
class ProcessingResult:
    """Result of document processing operation."""
    
    document_id: str
    status: str
    num_chunks: int
    error: Optional[str] = None
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate processing result.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.document_id or not self.document_id.strip():
            return False, "document_id cannot be empty"
        
        if not self.status or not self.status.strip():
            return False, "status cannot be empty"
        
        if self.num_chunks < 0:
            return False, "num_chunks cannot be negative"
        
        return True, None


@dataclass
class ErrorResponse:
    """Standard error response format."""
    
    error_code: str
    message: str
    details: Optional[str] = None
    retry_after: Optional[int] = None  # seconds
    correlation_id: str = ""
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate error response.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.error_code or not self.error_code.strip():
            return False, "error_code cannot be empty"
        
        if not self.message or not self.message.strip():
            return False, "message cannot be empty"
        
        if self.retry_after is not None and self.retry_after < 0:
            return False, "retry_after cannot be negative"
        
        return True, None
