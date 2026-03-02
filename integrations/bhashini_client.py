"""Bhashini ULCA API client for speech processing.

This module provides a wrapper for the Bhashini Universal Language Contribution API (ULCA)
for Speech-to-Text (STT) and Text-to-Speech (TTS) operations in Indian languages.
"""

import base64
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class STTResult:
    """Result from Speech-to-Text conversion."""
    text: str
    language: str
    confidence: float


@dataclass
class TTSResult:
    """Result from Text-to-Speech conversion."""
    audio: bytes
    language: str
    format: str  # audio format (e.g., 'wav', 'mp3')


class BhashiniClientError(Exception):
    """Base exception for Bhashini client errors."""
    pass


class BhashiniClient:
    """Client for interacting with Bhashini ULCA APIs.
    
    Bhashini ULCA (Universal Language Contribution API) provides speech processing
    capabilities for multiple Indian languages.
    """
    
    # Bhashini ULCA API endpoints
    ULCA_BASE_URL = "https://meity-auth.ulcacontrib.org"
    PIPELINE_ENDPOINT = "/ulca/apis/v0/model/getModelsPipeline"
    COMPUTE_ENDPOINT = "/ulca/apis/asr/v1/recognize"  # STT
    TTS_COMPUTE_ENDPOINT = "/ulca/apis/tts/v1/generate"  # TTS
    
    def __init__(self, ulca_api_key: str, ulca_user_id: str):
        """Initialize Bhashini client with credentials.
        
        Args:
            ulca_api_key: API key for Bhashini ULCA
            ulca_user_id: User ID for Bhashini ULCA
        """
        if not ulca_api_key or not ulca_api_key.strip():
            raise ValueError("ulca_api_key cannot be empty")
        if not ulca_user_id or not ulca_user_id.strip():
            raise ValueError("ulca_user_id cannot be empty")
        
        self.api_key = ulca_api_key
        self.user_id = ulca_user_id
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "ulcaApiKey": self.api_key,
            "userID": self.user_id
        })
    
    def speech_to_text(
        self,
        audio: bytes,
        source_language: str,
        audio_format: str = "wav",
        sample_rate: int = 16000
    ) -> STTResult:
        """Convert speech to text using Bhashini ULCA STT API.
        
        Args:
            audio: Audio data in bytes
            source_language: Source language code (e.g., 'hi', 'en', 'ta')
            audio_format: Audio format (default: 'wav')
            sample_rate: Audio sample rate in Hz (default: 16000)
        
        Returns:
            STTResult containing transcribed text, language, and confidence
        
        Raises:
            BhashiniClientError: If the API call fails
        """
        if not audio or len(audio) == 0:
            raise ValueError("audio cannot be empty")
        if not source_language or not source_language.strip():
            raise ValueError("source_language cannot be empty")
        
        try:
            # Step 1: Get pipeline configuration for STT
            pipeline_config = self._get_stt_pipeline_config(source_language)
            
            # Step 2: Encode audio to base64
            audio_base64 = base64.b64encode(audio).decode('utf-8')
            
            # Step 3: Prepare STT request
            compute_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": source_language
                            },
                            "serviceId": pipeline_config.get("serviceId"),
                            "audioFormat": audio_format,
                            "samplingRate": sample_rate
                        }
                    }
                ],
                "inputData": {
                    "audio": [
                        {
                            "audioContent": audio_base64
                        }
                    ]
                }
            }
            
            # Step 4: Call compute endpoint
            compute_url = pipeline_config.get("callbackUrl", self.ULCA_BASE_URL + self.COMPUTE_ENDPOINT)
            response = self.session.post(
                compute_url,
                json=compute_payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Step 5: Parse response with robust error handling
            result = response.json()
            
            # Validate response structure
            if "pipelineResponse" not in result:
                raise BhashiniClientError(f"Invalid response format from Bhashini STT API. Response: {result}")
            
            # Handle empty pipelineResponse
            if not result["pipelineResponse"] or len(result["pipelineResponse"]) == 0:
                raise BhashiniClientError("Empty pipelineResponse received from Bhashini API")
            
            # Extract output with multiple fallback paths
            pipeline_output = result["pipelineResponse"][0]
            
            # Try different possible response structures
            transcribed_text = None
            
            # Path 1: output[0].source
            if "output" in pipeline_output and pipeline_output["output"]:
                if len(pipeline_output["output"]) > 0:
                    transcribed_text = pipeline_output["output"][0].get("source", "")
            
            # Path 2: audio[0].source (alternative structure)
            if not transcribed_text and "audio" in pipeline_output:
                if pipeline_output["audio"] and len(pipeline_output["audio"]) > 0:
                    transcribed_text = pipeline_output["audio"][0].get("source", "")
            
            # Path 3: Direct source field
            if not transcribed_text:
                transcribed_text = pipeline_output.get("source", "")
            
            # Validate transcribed text
            if not transcribed_text or not transcribed_text.strip():
                raise BhashiniClientError("Empty transcription received from Bhashini API. The audio may be unclear or too quiet.")
            
            return STTResult(
                text=transcribed_text.strip(),
                language=source_language,
                confidence=1.0  # ULCA doesn't always provide confidence scores
            )
        
        except requests.RequestException as e:
            raise BhashiniClientError(f"STT API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise BhashiniClientError(f"Failed to parse STT response: {str(e)}")
    
    def text_to_speech(
        self,
        text: str,
        target_language: str,
        gender: str = "female",
        sample_rate: int = 16000
    ) -> TTSResult:
        """Convert text to speech using Bhashini ULCA TTS API.
        
        Args:
            text: Text to convert to speech
            target_language: Target language code (e.g., 'hi', 'en', 'ta')
            gender: Voice gender ('male' or 'female', default: 'female')
            sample_rate: Audio sample rate in Hz (default: 16000)
        
        Returns:
            TTSResult containing audio bytes, language, and format
        
        Raises:
            BhashiniClientError: If the API call fails
        """
        if not text or not text.strip():
            raise ValueError("text cannot be empty")
        if not target_language or not target_language.strip():
            raise ValueError("target_language cannot be empty")
        
        try:
            # Step 1: Get pipeline configuration for TTS
            pipeline_config = self._get_tts_pipeline_config(target_language)
            
            # Step 2: Prepare TTS request
            compute_payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": target_language
                            },
                            "serviceId": pipeline_config.get("serviceId"),
                            "gender": gender,
                            "samplingRate": sample_rate
                        }
                    }
                ],
                "inputData": {
                    "input": [
                        {
                            "source": text
                        }
                    ]
                }
            }
            
            # Step 3: Call compute endpoint
            compute_url = pipeline_config.get("callbackUrl", self.ULCA_BASE_URL + self.TTS_COMPUTE_ENDPOINT)
            response = self.session.post(
                compute_url,
                json=compute_payload,
                timeout=30
            )
            response.raise_for_status()
            
            # Step 4: Parse response
            result = response.json()
            
            if "pipelineResponse" not in result:
                raise BhashiniClientError("Invalid response format from Bhashini TTS API")
            
            output = result["pipelineResponse"][0].get("audio", [{}])[0]
            audio_base64 = output.get("audioContent", "")
            
            if not audio_base64:
                raise BhashiniClientError("Empty audio received from Bhashini API")
            
            # Step 5: Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            return TTSResult(
                audio=audio_bytes,
                language=target_language,
                format="wav"
            )
        
        except requests.RequestException as e:
            raise BhashiniClientError(f"TTS API request failed: {str(e)}")
        except (KeyError, IndexError) as e:
            raise BhashiniClientError(f"Failed to parse TTS response: {str(e)}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported Indian languages from ULCA.
        
        Returns:
            List of language codes supported by Bhashini
        """
        # Common Indian languages supported by Bhashini ULCA
        return [
            "hi",  # Hindi
            "en",  # English
            "bn",  # Bengali
            "ta",  # Tamil
            "te",  # Telugu
            "mr",  # Marathi
            "gu",  # Gujarati
            "kn",  # Kannada
            "ml",  # Malayalam
            "pa",  # Punjabi
            "or",  # Odia
            "as",  # Assamese
        ]
    
    def _get_stt_pipeline_config(self, language: str) -> Dict[str, Any]:
        """Get pipeline configuration for STT.
        
        Args:
            language: Language code
        
        Returns:
            Pipeline configuration dictionary
        
        Raises:
            BhashiniClientError: If pipeline configuration fails
        """
        try:
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "asr",
                        "config": {
                            "language": {
                                "sourceLanguage": language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            }
            
            response = self.session.post(
                self.ULCA_BASE_URL + self.PIPELINE_ENDPOINT,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "pipelineResponseConfig" not in result:
                raise BhashiniClientError("Invalid pipeline configuration response")
            
            return result["pipelineResponseConfig"][0]
        
        except requests.RequestException as e:
            raise BhashiniClientError(f"Failed to get STT pipeline config: {str(e)}")
    
    def _get_tts_pipeline_config(self, language: str) -> Dict[str, Any]:
        """Get pipeline configuration for TTS.
        
        Args:
            language: Language code
        
        Returns:
            Pipeline configuration dictionary
        
        Raises:
            BhashiniClientError: If pipeline configuration fails
        """
        try:
            payload = {
                "pipelineTasks": [
                    {
                        "taskType": "tts",
                        "config": {
                            "language": {
                                "sourceLanguage": language
                            }
                        }
                    }
                ],
                "pipelineRequestConfig": {
                    "pipelineId": "64392f96daac500b55c543cd"
                }
            }
            
            response = self.session.post(
                self.ULCA_BASE_URL + self.PIPELINE_ENDPOINT,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "pipelineResponseConfig" not in result:
                raise BhashiniClientError("Invalid pipeline configuration response")
            
            return result["pipelineResponseConfig"][0]
        
        except requests.RequestException as e:
            raise BhashiniClientError(f"Failed to get TTS pipeline config: {str(e)}")
