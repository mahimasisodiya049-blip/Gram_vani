"""Unit tests for data models.

Tests edge cases, validation error messages, and specific scenarios.
Requirements: 1.2, 2.4
"""

import pytest
from datetime import datetime
from models import (
    DocumentMetadata,
    TextChunk,
    QueryResult,
    UploadResult,
    TranscriptionResult,
    ProcessingResult,
    ErrorResponse
)


class TestDocumentMetadata:
    """Unit tests for DocumentMetadata model."""
    
    def test_valid_document_metadata(self):
        """Test valid document metadata passes validation."""
        metadata = DocumentMetadata(
            document_id="doc123",
            user_id="user456",
            filename="test.pdf",
            s3_key="uploads/test.pdf",
            upload_timestamp=datetime.now(),
            processing_status="completed",
            num_pages=5,
            num_chunks=10
        )
        is_valid, error = metadata.validate()
        assert is_valid
        assert error is None
    
    def test_empty_document_id(self):
        """Test empty document_id fails validation."""
        metadata = DocumentMetadata(
            document_id="",
            user_id="user456",
            filename="test.pdf",
            s3_key="uploads/test.pdf",
            upload_timestamp=datetime.now(),
            processing_status="completed",
            num_pages=5,
            num_chunks=10
        )
        is_valid, error = metadata.validate()
        assert not is_valid
        assert error == "document_id cannot be empty"
    
    def test_whitespace_only_user_id(self):
        """Test whitespace-only user_id fails validation."""
        metadata = DocumentMetadata(
            document_id="doc123",
            user_id="   ",
            filename="test.pdf",
            s3_key="uploads/test.pdf",
            upload_timestamp=datetime.now(),
            processing_status="completed",
            num_pages=5,
            num_chunks=10
        )
        is_valid, error = metadata.validate()
        assert not is_valid
        assert error == "user_id cannot be empty"
    
    def test_invalid_processing_status(self):
        """Test invalid processing_status fails validation."""
        metadata = DocumentMetadata(
            document_id="doc123",
            user_id="user456",
            filename="test.pdf",
            s3_key="uploads/test.pdf",
            upload_timestamp=datetime.now(),
            processing_status="invalid_status",
            num_pages=5,
            num_chunks=10
        )
        is_valid, error = metadata.validate()
        assert not is_valid
        assert "processing_status must be one of" in error
    
    def test_negative_num_pages(self):
        """Test negative num_pages fails validation."""
        metadata = DocumentMetadata(
            document_id="doc123",
            user_id="user456",
            filename="test.pdf",
            s3_key="uploads/test.pdf",
            upload_timestamp=datetime.now(),
            processing_status="completed",
            num_pages=-1,
            num_chunks=10
        )
        is_valid, error = metadata.validate()
        assert not is_valid
        assert error == "num_pages cannot be negative"


class TestTextChunk:
    """Unit tests for TextChunk model."""
    
    def test_valid_text_chunk(self):
        """Test valid text chunk passes validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="Sample text content",
            page_number=1,
            chunk_index=0
        )
        is_valid, error = chunk.validate()
        assert is_valid
        assert error is None
    
    def test_empty_text(self):
        """Test empty text fails validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="",
            page_number=1,
            chunk_index=0
        )
        is_valid, error = chunk.validate()
        assert not is_valid
        assert error == "text cannot be empty"
    
    def test_negative_page_number(self):
        """Test negative page_number fails validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="Sample text",
            page_number=-1,
            chunk_index=0
        )
        is_valid, error = chunk.validate()
        assert not is_valid
        assert error == "page_number cannot be negative"
    
    def test_empty_embedding_list(self):
        """Test empty embedding list fails validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="Sample text",
            page_number=1,
            chunk_index=0,
            embedding=[]
        )
        is_valid, error = chunk.validate()
        assert not is_valid
        assert error == "embedding cannot be empty list"
    
    def test_valid_embedding(self):
        """Test valid embedding passes validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="Sample text",
            page_number=1,
            chunk_index=0,
            embedding=[0.1, 0.2, 0.3]
        )
        is_valid, error = chunk.validate()
        assert is_valid
        assert error is None


class TestUploadResult:
    """Unit tests for UploadResult model."""
    
    def test_successful_upload(self):
        """Test successful upload result passes validation."""
        result = UploadResult(
            upload_id="upload123",
            status="success",
            message="Upload successful",
            document_id="doc456"
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None
    
    def test_failed_upload_without_document_id(self):
        """Test failed upload without document_id passes validation."""
        result = UploadResult(
            upload_id="upload123",
            status="failed",
            message="Upload failed"
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None
    
    def test_success_without_document_id(self):
        """Test success status without document_id fails validation."""
        result = UploadResult(
            upload_id="upload123",
            status="success",
            message="Upload successful"
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "document_id is required when status is success"
    
    def test_invalid_status(self):
        """Test invalid status fails validation."""
        result = UploadResult(
            upload_id="upload123",
            status="pending",
            message="Upload pending"
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert "status must be one of" in error


class TestTranscriptionResult:
    """Unit tests for TranscriptionResult model."""
    
    def test_valid_transcription(self):
        """Test valid transcription passes validation."""
        result = TranscriptionResult(
            text="Hello world",
            language="en",
            confidence=0.95
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None
    
    def test_empty_text(self):
        """Test empty text fails validation."""
        result = TranscriptionResult(
            text="",
            language="en",
            confidence=0.95
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "text cannot be empty"
    
    def test_confidence_below_zero(self):
        """Test confidence below 0.0 fails validation."""
        result = TranscriptionResult(
            text="Hello",
            language="en",
            confidence=-0.1
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "confidence must be between 0.0 and 1.0"
    
    def test_confidence_above_one(self):
        """Test confidence above 1.0 fails validation."""
        result = TranscriptionResult(
            text="Hello",
            language="en",
            confidence=1.5
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "confidence must be between 0.0 and 1.0"


class TestProcessingResult:
    """Unit tests for ProcessingResult model."""
    
    def test_valid_processing_result(self):
        """Test valid processing result passes validation."""
        result = ProcessingResult(
            document_id="doc123",
            status="completed",
            num_chunks=10
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None
    
    def test_negative_num_chunks(self):
        """Test negative num_chunks fails validation."""
        result = ProcessingResult(
            document_id="doc123",
            status="completed",
            num_chunks=-5
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "num_chunks cannot be negative"
    
    def test_with_error_message(self):
        """Test processing result with error message."""
        result = ProcessingResult(
            document_id="doc123",
            status="failed",
            num_chunks=0,
            error="PDF extraction failed"
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None


class TestErrorResponse:
    """Unit tests for ErrorResponse model."""
    
    def test_valid_error_response(self):
        """Test valid error response passes validation."""
        response = ErrorResponse(
            error_code="ERR001",
            message="An error occurred",
            correlation_id="corr123"
        )
        is_valid, error = response.validate()
        assert is_valid
        assert error is None
    
    def test_empty_error_code(self):
        """Test empty error_code fails validation."""
        response = ErrorResponse(
            error_code="",
            message="An error occurred"
        )
        is_valid, error = response.validate()
        assert not is_valid
        assert error == "error_code cannot be empty"
    
    def test_negative_retry_after(self):
        """Test negative retry_after fails validation."""
        response = ErrorResponse(
            error_code="ERR001",
            message="Service unavailable",
            retry_after=-10
        )
        is_valid, error = response.validate()
        assert not is_valid
        assert error == "retry_after cannot be negative"
    
    def test_with_details(self):
        """Test error response with details."""
        response = ErrorResponse(
            error_code="ERR001",
            message="Validation failed",
            details="Field 'name' is required",
            correlation_id="corr456"
        )
        is_valid, error = response.validate()
        assert is_valid
        assert error is None


class TestQueryResult:
    """Unit tests for QueryResult model."""
    
    def test_valid_query_result(self):
        """Test valid query result passes validation."""
        chunk = TextChunk(
            chunk_id="chunk1",
            document_id="doc123",
            text="Sample text",
            page_number=1,
            chunk_index=0
        )
        result = QueryResult(
            query_id="query123",
            query_text="What is this?",
            answer_text="This is a sample answer",
            answer_audio=b"audio_data",
            language="en",
            retrieved_chunks=[chunk],
            processing_time_ms=1500
        )
        is_valid, error = result.validate()
        assert is_valid
        assert error is None
    
    def test_empty_query_id(self):
        """Test empty query_id fails validation."""
        result = QueryResult(
            query_id="",
            query_text="What is this?",
            answer_text="Answer",
            answer_audio=b"audio",
            language="en",
            retrieved_chunks=[],
            processing_time_ms=1000
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "query_id cannot be empty"
    
    def test_empty_answer_audio(self):
        """Test empty answer_audio fails validation."""
        result = QueryResult(
            query_id="query123",
            query_text="What is this?",
            answer_text="Answer",
            answer_audio=b"",
            language="en",
            retrieved_chunks=[],
            processing_time_ms=1000
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "answer_audio cannot be empty"
    
    def test_negative_processing_time(self):
        """Test negative processing_time_ms fails validation."""
        result = QueryResult(
            query_id="query123",
            query_text="What is this?",
            answer_text="Answer",
            answer_audio=b"audio",
            language="en",
            retrieved_chunks=[],
            processing_time_ms=-100
        )
        is_valid, error = result.validate()
        assert not is_valid
        assert error == "processing_time_ms cannot be negative"
