"""Integration layer for external services."""

from .bhashini_client import BhashiniClient

# Try to import AWS clients, but make them optional
try:
    from .aws_client import BedrockClient, RAGEngine, AWSClientError
    AWS_AVAILABLE = True
except ImportError:
    # AWS dependencies not installed
    AWS_AVAILABLE = False
    BedrockClient = None
    RAGEngine = None
    AWSClientError = Exception

__all__ = [
    "BhashiniClient",
    "BedrockClient", 
    "RAGEngine",
    "AWSClientError",
    "AWS_AVAILABLE"
]
