"""AWS integration layer for S3 and Bedrock services.

This module provides clients for interacting with AWS services:
- S3Client: For document storage and retrieval
- BedrockClient: For embeddings and LLM generation with Claude 3.5 Sonnet
- RAGEngine: For retrieval-augmented generation with fallback handling
"""

import boto3
import json
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, BotoCoreError
import logging

logger = logging.getLogger(__name__)


class AWSClientError(Exception):
    """Base exception for AWS client errors."""
    pass


class BedrockClient:
    """Client for AWS Bedrock operations with Claude 3.5 Sonnet."""
    
    # Model IDs
    CLAUDE_3_5_SONNET = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    TITAN_EMBED_TEXT_V1 = "amazon.titan-embed-text-v1"
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize Bedrock client.
        
        Args:
            region_name: AWS region (default: us-east-1)
        """
        self.region_name = region_name
        
        try:
            self.runtime_client = boto3.client(
                'bedrock-runtime',
                region_name=region_name
            )
            logger.info(f"Bedrock client initialized in region: {region_name}")
        except Exception as e:
            raise AWSClientError(f"Failed to initialize Bedrock client: {str(e)}")
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model_id: str = CLAUDE_3_5_SONNET,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """Generate text using Claude 3.5 Sonnet model.
        
        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt for context
            model_id: Bedrock model ID (default: Claude 3.5 Sonnet)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            top_p: Nucleus sampling parameter
        
        Returns:
            Generated text response
        
        Raises:
            AWSClientError: If generation fails
        """
        try:
            # Prepare request body for Claude 3.5 Sonnet
            # CRITICAL: Use correct format for Anthropic models
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Add system prompt if provided (separate field, not in messages)
            if system_prompt:
                body["system"] = system_prompt
            
            logger.debug(f"Bedrock request to model: {model_id}")
            logger.debug(f"Request body: {json.dumps(body, indent=2)}")
            
            # Call Bedrock API
            response = self.runtime_client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            logger.debug(f"Bedrock response: {json.dumps(response_body, indent=2)}")
            
            # Extract text from response
            # Claude 3.5 Sonnet returns: content[0].text
            if 'content' in response_body and len(response_body['content']) > 0:
                generated_text = response_body['content'][0]['text']
                logger.info(f"Generated {len(generated_text)} characters")
                return generated_text
            else:
                raise AWSClientError("No content in Bedrock response")
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Bedrock API error: {error_code} - {error_message}")
            raise AWSClientError(f"Bedrock API error ({error_code}): {error_message}")
        
        except (BotoCoreError, KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to generate text: {str(e)}")
            raise AWSClientError(f"Failed to generate text with Bedrock: {str(e)}")


class RAGEngine:
    """RAG (Retrieval-Augmented Generation) engine with fallback handling."""
    
    def __init__(self, bedrock_client: BedrockClient):
        """Initialize RAG engine.
        
        Args:
            bedrock_client: Bedrock client for LLM generation
        """
        self.bedrock_client = bedrock_client
        logger.info("RAG engine initialized")
    
    def generate_answer(
        self,
        question: str,
        context: Optional[str] = None,
        language: str = "en"
    ) -> str:
        """Generate answer using RAG approach with fallback handling.
        
        Args:
            question: User's question
            context: Retrieved context from documents (optional)
            language: Language code for response
        
        Returns:
            Generated answer text (never fails, uses fallback if needed)
        """
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(language)
            
            # Build user prompt with or without context
            if context and context.strip():
                user_prompt = self._build_prompt_with_context(question, context)
                logger.info(f"Generating answer WITH context ({len(context)} chars)")
            else:
                user_prompt = self._build_prompt_without_context(question)
                logger.info("Generating answer WITHOUT context (no documents)")
            
            logger.info(f"Question: {question[:100]}...")
            
            # Generate answer
            answer = self.bedrock_client.generate_text(
                prompt=user_prompt,
                system_prompt=system_prompt,
                max_tokens=1024,
                temperature=0.3  # Lower temperature for factual responses
            )
            
            return answer
        
        except AWSClientError as e:
            logger.error(f"RAG generation failed: {str(e)}")
            # Return fallback message instead of raising
            return self._get_fallback_message(language)
        
        except Exception as e:
            logger.error(f"Unexpected error in RAG generation: {str(e)}")
            return self._get_fallback_message(language)
    
    def retrieve_context(self, question: str, top_k: int = 3) -> Optional[str]:
        """Retrieve relevant context from documents.
        
        This is a placeholder for vector search implementation.
        
        Args:
            question: User's question
            top_k: Number of top chunks to retrieve
        
        Returns:
            Retrieved context or None if retrieval fails
        """
        try:
            # TODO: Implement vector search
            # For now, return None to trigger fallback
            logger.warning("Vector search not implemented yet - returning None")
            return None
        
        except Exception as e:
            logger.error(f"Context retrieval failed: {str(e)}")
            return None
    
    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt based on language."""
        prompts = {
            "hi": """आप एक सहायक सहायक हैं जो सरकारी दस्तावेज़ों को सरल भाषा में समझाते हैं।
आपका काम जटिल सरकारी जानकारी को आम लोगों के लिए समझने योग्य बनाना है।
केवल दिए गए संदर्भ के आधार पर उत्तर दें। यदि जानकारी उपलब्ध नहीं है, तो स्पष्ट रूप से बताएं।""",
            
            "en": """You are a helpful assistant that explains government documents in simple language.
Your job is to make complex government information understandable for common people.
Answer only based on the provided context. If information is not available, clearly state that.""",
            
            "ta": """நீங்கள் அரசாங்க ஆவணங்களை எளிய மொழியில் விளக்கும் உதவியாளர்.
சிக்கலான அரசாங்க தகவல்களை சாதாரண மக்களுக்கு புரியும்படி செய்வது உங்கள் வேலை.
வழங்கப்பட்ட சூழலின் அடிப்படையில் மட்டுமே பதிலளிக்கவும்."""
        }
        
        return prompts.get(language, prompts["en"])
    
    def _build_prompt_with_context(self, question: str, context: str) -> str:
        """Build prompt with retrieved context."""
        return f"""Based on the following context from government documents, please answer the question.

Context:
{context}

Question: {question}

Please provide a clear, simple answer based only on the information in the context above. If the context doesn't contain enough information to answer the question, please say so."""
    
    def _build_prompt_without_context(self, question: str) -> str:
        """Build prompt when no context is available."""
        return f"""Question: {question}

Note: No relevant documents were found to answer this question. Please provide a helpful response explaining that the information is not available in the uploaded documents and suggest what the user should do."""
    
    def _get_fallback_message(self, language: str) -> str:
        """Get fallback message when generation fails."""
        messages = {
            "hi": """क्षमा करें, मैं अभी आपके सवाल का जवाब नहीं दे सकता। कृपया बाद में पुनः प्रयास करें या अपने प्रश्न को अलग तरीके से पूछें।

यदि समस्या बनी रहती है, तो कृपया जांचें:
- क्या प्रासंगिक दस्तावेज़ अपलोड किए गए हैं
- क्या आपका इंटरनेट कनेक्शन काम कर रहा है
- क्या AWS सेवाएं उपलब्ध हैं""",
            
            "en": """Sorry, I cannot answer your question right now. Please try again later or rephrase your question.

If the problem persists, please check:
- Are relevant documents uploaded
- Is your internet connection working
- Are AWS services available""",
            
            "ta": """மன்னிக்கவும், இப்போது உங்கள் கேள்விக்கு பதிலளிக்க முடியவில்லை. பிறகு முயற்சிக்கவும் அல்லது உங்கள் கேள்வியை வேறு விதமாக கேளுங்கள்.

பிரச்சனை தொடர்ந்தால், தயவுசெய்து சரிபார்க்கவும்:
- தொடர்புடைய ஆவணங்கள் பதிவேற்றப்பட்டுள்ளதா
- உங்கள் இணைய இணைப்பு வேலை செய்கிறதா
- AWS சேவைகள் கிடைக்குமா"""
        }
        
        return messages.get(language, messages["en"])
