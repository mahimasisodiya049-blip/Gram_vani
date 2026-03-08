"""Bhashini Dhruva API client for speech processing.

This module provides a wrapper for the Bhashini Dhruva inference API
for Speech-to-Text (STT) and Text-to-Speech (TTS) in Indian languages.
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
    """Client for interacting with Bhashini Dhruva inference APIs.

    Uses the Dhruva pipeline endpoint which is the current production API.
    Auth: Authorization header with the ULCA API key.
    """

    # Current Bhashini Dhruva inference endpoint
    DHRUVA_BASE_URL = "https://dhruva-api.bhashini.gov.in"
    PIPELINE_ENDPOINT = "/services/inference/pipeline"

    # Pipeline IDs for different tasks
    ASR_SERVICE_ID = "ai4bharat/conformer-hi-gpu--t4"   # default Hindi ASR
    TTS_SERVICE_ID = "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"  # Hindi TTS

    # Map from short language code to full BCP-47 tag used by Bhashini
    LANGUAGE_MAP = {
        "hi": "hi",
        "en": "en",
        "ta": "ta",
        "te": "te",
        "bn": "bn",
        "mr": "mr",
        "gu": "gu",
        "kn": "kn",
        "ml": "ml",
        "pa": "pa",
        "or": "or",
        "as": "as",
    }

    def __init__(self, ulca_api_key: str, ulca_user_id: str):
        """Initialize Bhashini client with credentials.

        Args:
            ulca_api_key: API key for Bhashini (used as Authorization token)
            ulca_user_id: User ID for Bhashini ULCA (kept for compatibility)
        """
        if not ulca_api_key or not ulca_api_key.strip():
            raise ValueError("ulca_api_key cannot be empty")
        if not ulca_user_id or not ulca_user_id.strip():
            raise ValueError("ulca_user_id cannot be empty")

        self.api_key = ulca_api_key
        self.user_id = ulca_user_id
        self.session = requests.Session()
        # Dhruva API uses Authorization header (not ulcaApiKey)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": self.api_key,
            "userID": self.user_id,
        })

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def speech_to_text(
        self,
        audio: bytes,
        source_language: str,
        audio_format: str = "wav",
        sample_rate: int = 16000,
    ) -> STTResult:
        """Convert speech to text using Bhashini Dhruva ASR pipeline.

        Args:
            audio: Audio data in bytes
            source_language: Short language code (e.g. 'hi', 'en', 'ta')
            audio_format: Audio format (default: 'wav')
            sample_rate: Audio sample rate in Hz (default: 16000)

        Returns:
            STTResult with transcribed text, language, and confidence

        Raises:
            BhashiniClientError: If the API call fails or no text returned
        """
        if not audio or len(audio) == 0:
            raise ValueError("audio cannot be empty")
        if not source_language or not source_language.strip():
            raise ValueError("source_language cannot be empty")

        lang = self.LANGUAGE_MAP.get(source_language, source_language)
        audio_base64 = base64.b64encode(audio).decode("utf-8")

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {"sourceLanguage": lang},
                        "audioFormat": audio_format,
                        "samplingRate": sample_rate,
                        "postProcessors": ["itn"],
                    },
                }
            ],
            "inputData": {
                "audio": [{"audioContent": audio_base64}]
            },
        }

        try:
            response = self.session.post(
                self.DHRUVA_BASE_URL + self.PIPELINE_ENDPOINT,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            raise BhashiniClientError(
                f"Bhashini ASR HTTP {response.status_code}: {response.text[:300]}"
            ) from e
        except requests.RequestException as e:
            raise BhashiniClientError(f"STT API request failed: {str(e)}") from e

        result = response.json()

        # --- Parse response ---
        transcribed_text = self._extract_stt_text(result)
        if not transcribed_text or not transcribed_text.strip():
            raise BhashiniClientError(
                "Empty transcription received from Bhashini API. "
                "The audio may be unclear or too quiet."
            )

        return STTResult(
            text=transcribed_text.strip(),
            language=source_language,
            confidence=1.0,
        )

    def text_to_speech(
        self,
        text: str,
        target_language: str,
        gender: str = "female",
        sample_rate: int = 8000,
    ) -> TTSResult:
        """Convert text to speech using Bhashini Dhruva TTS pipeline.

        Args:
            text: Text to convert to speech
            target_language: Short language code (e.g. 'hi', 'en', 'ta')
            gender: Voice gender ('male' or 'female', default: 'female')
            sample_rate: Audio sample rate in Hz (default: 8000)

        Returns:
            TTSResult with audio bytes, language, and format

        Raises:
            BhashiniClientError: If the API call fails
        """
        if not text or not text.strip():
            raise ValueError("text cannot be empty")
        if not target_language or not target_language.strip():
            raise ValueError("target_language cannot be empty")

        lang = self.LANGUAGE_MAP.get(target_language, target_language)

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {"sourceLanguage": lang},
                        "gender": gender,
                        "samplingRate": sample_rate,
                    },
                }
            ],
            "inputData": {
                "input": [{"source": text}]
            },
        }

        try:
            response = self.session.post(
                self.DHRUVA_BASE_URL + self.PIPELINE_ENDPOINT,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            raise BhashiniClientError(
                f"Bhashini TTS HTTP {response.status_code}: {response.text[:300]}"
            ) from e
        except requests.RequestException as e:
            raise BhashiniClientError(f"TTS API request failed: {str(e)}") from e

        result = response.json()

        # --- Parse response ---
        audio_base64 = self._extract_tts_audio(result)
        if not audio_base64:
            raise BhashiniClientError("Empty audio received from Bhashini TTS API")

        audio_bytes = base64.b64decode(audio_base64)
        return TTSResult(audio=audio_bytes, language=target_language, format="wav")

    def get_supported_languages(self) -> List[str]:
        """Return list of supported language codes."""
        return list(self.LANGUAGE_MAP.keys())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_stt_text(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract transcribed text from Dhruva pipeline response."""
        try:
            pipeline_response = result.get("pipelineResponse", [])
            if not pipeline_response:
                return None

            task_output = pipeline_response[0]

            # Path 1: output[0].source  (most common)
            outputs = task_output.get("output", [])
            if outputs:
                return outputs[0].get("source", "")

            # Path 2: audio[0].source
            audio_items = task_output.get("audio", [])
            if audio_items:
                return audio_items[0].get("source", "")

            # Path 3: direct source
            return task_output.get("source", "")

        except (KeyError, IndexError):
            return None

    def _extract_tts_audio(self, result: Dict[str, Any]) -> Optional[str]:
        """Extract base64 audio content from Dhruva pipeline response."""
        try:
            pipeline_response = result.get("pipelineResponse", [])
            if not pipeline_response:
                return None

            audio_list = pipeline_response[0].get("audio", [])
            if not audio_list:
                return None

            return audio_list[0].get("audioContent", "")

        except (KeyError, IndexError):
            return None
