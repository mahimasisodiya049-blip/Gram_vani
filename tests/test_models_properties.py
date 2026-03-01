"""Property-based tests for data models.

Feature: gram-vani
"""

from hypothesis import given, strategies as st
from models import TranscriptionResult


# Feature: gram-vani, Property 8: Transcription validation
# Validates: Requirements 3.2
@given(
    text=st.text(min_size=1),
    language=st.text(min_size=1),
    confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_transcription_validation_property(text, language, confidence):
    """
    **Property 8: Transcription validation**
    **Validates: Requirements 3.2**
    
    For any transcription result from Voice_Processor, the system should validate
    that the text is non-empty before proceeding with query processing.
    
    This property verifies that:
    1. Non-empty text with valid language and confidence passes validation
    2. The validation method correctly identifies valid transcription results
    """
    result = TranscriptionResult(
        text=text,
        language=language,
        confidence=confidence
    )
    
    is_valid, error_msg = result.validate()
    
    # For non-empty text and language with valid confidence, validation should pass
    if text.strip() and language.strip():
        assert is_valid, f"Expected valid transcription to pass validation, but got error: {error_msg}"
        assert error_msg is None
    else:
        # Empty text or language should fail validation
        assert not is_valid
        assert error_msg is not None
