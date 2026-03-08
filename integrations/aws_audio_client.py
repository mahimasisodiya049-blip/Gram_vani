"""AWS Audio Client for Speech-to-Text and Text-to-Speech.

This module provides audio processing using AWS services:
- Amazon Transcribe: For speech-to-text (STT)
- Amazon Polly: For text-to-speech (TTS) with Indian voices
"""

import boto3
import json
import time
import uuid
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, BotoCoreError
import logging
import io

logger = logging.getLogger(__name__)


class AWSAudioClientError(Exception):
    """Base exception for AWS audio client errors."""
    pass


class AWSAudioClient:
    """Client for AWS Transcribe and Polly operations."""
    
    # Supported languages and their Polly voices
    LANGUAGE_VOICES = {
        'hi': {'voice': 'Aditi', 'engine': 'neural'},  # Hindi - Female
        'hi-male': {'voice': 'Madhav', 'engine': 'standard'},  # Hindi - Male
        'en': {'voice': 'Joanna', 'engine': 'neural'},  # English - Female
        'en-IN': {'voice': 'Aditi', 'engine': 'neural'},  # Indian English
        'ta': {'voice': 'Joanna', 'engine': 'neural'},  # Tamil (fallback to English)
        'te': {'voice': 'Joanna', 'engine': 'neural'},  # Telugu (fallback to English)
        'bn': {'voice': 'Joanna', 'engine': 'neural'},  # Bengali (fallback to English)
    }

    # Correct Polly LanguageCode for each voice — must match the voice, not the user language
    POLLY_LANGUAGE_CODES = {
        'Aditi':  'hi-IN',
        'Madhav': 'hi-IN',
        'Joanna': 'en-US',
        'Raveena': 'en-IN',
    }
    
    # Language codes for Transcribe
    TRANSCRIBE_LANGUAGES = {
        'hi': 'hi-IN',
        'en': 'en-US',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'bn': 'bn-IN',
        'mr': 'en-IN',  # Marathi - fallback to Indian English
        'gu': 'en-IN',  # Gujarati - fallback to Indian English
        'kn': 'en-IN',  # Kannada - fallback to Indian English
    }
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize AWS audio clients.
        
        Args:
            region_name: AWS region (default: us-east-1)
        """
        self.region_name = region_name
        
        try:
            # Initialize Transcribe client
            self.transcribe_client = boto3.client(
                'transcribe',
                region_name=region_name
            )
            
            # Initialize Polly client
            self.polly_client = boto3.client(
                'polly',
                region_name=region_name
            )
            
            # Initialize S3 client for Transcribe (needs S3 for audio storage)
            self.s3_client = boto3.client(
                's3',
                region_name=region_name
            )
            
            logger.info(f"AWS audio clients initialized in region: {region_name}")
        
        except Exception as e:
            raise AWSAudioClientError(f"Failed to initialize AWS audio clients: {str(e)}")
    
    def speech_to_text(
        self,
        audio: bytes,
        language: str = "hi",
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """Convert speech to text using Amazon Transcribe.
        
        Args:
            audio: Audio data in bytes
            language: Language code (hi, en, ta, te, bn, etc.)
            audio_format: Audio format (wav, mp3, etc.)
        
        Returns:
            Dictionary with 'text', 'language', and 'confidence'
        
        Raises:
            AWSAudioClientError: If transcription fails
        """
        if not audio or len(audio) == 0:
            raise ValueError("audio cannot be empty")
        
        # Get Transcribe language code
        transcribe_lang = self.TRANSCRIBE_LANGUAGES.get(language, 'hi-IN')
        
        # Generate unique job name
        job_name = f"transcribe-{uuid.uuid4().hex[:8]}-{int(time.time())}"
        
        # S3 bucket for temporary audio storage (you can configure this)
        bucket_name = f"gram-vani-transcribe-{self.region_name}"
        audio_key = f"audio/{job_name}.{audio_format}"
        
        try:
            # Step 1: Upload audio to S3 (Transcribe requires S3 URI)
            logger.info(f"Uploading audio to S3: s3://{bucket_name}/{audio_key}")
            
            try:
                # Try to create bucket if it doesn't exist
                try:
                    self.s3_client.head_bucket(Bucket=bucket_name)
                except ClientError:
                    # Bucket doesn't exist, create it
                    if self.region_name == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region_name}
                        )
                    logger.info(f"Created S3 bucket: {bucket_name}")
                
                # Upload audio file
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=audio_key,
                    Body=audio,
                    ContentType=f'audio/{audio_format}'
                )
            
            except ClientError as e:
                logger.error(f"S3 upload failed: {str(e)}")
                raise AWSAudioClientError(f"Failed to upload audio to S3: {str(e)}")
            
            # Step 2: Start transcription job
            logger.info(f"Starting transcription job: {job_name}")
            
            media_format = 'wav' if audio_format == 'wav' else audio_format
            
            self.transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': f's3://{bucket_name}/{audio_key}'},
                MediaFormat=media_format,
                LanguageCode=transcribe_lang
            )
            
            # Step 3: Wait for transcription to complete
            logger.info("Waiting for transcription to complete...")
            max_wait = 60  # Maximum 60 seconds
            wait_time = 0
            
            while wait_time < max_wait:
                response = self.transcribe_client.get_transcription_job(
                    TranscriptionJobName=job_name
                )
                
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    logger.info("Transcription completed successfully")
                    
                    # Get transcript
                    transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
                    
                    # Download transcript (it's a JSON file)
                    import urllib.request
                    with urllib.request.urlopen(transcript_uri) as response:
                        transcript_data = json.loads(response.read().decode())
                    
                    # Extract text
                    transcribed_text = transcript_data['results']['transcripts'][0]['transcript']
                    
                    # Get confidence (average of all items)
                    items = transcript_data['results'].get('items', [])
                    confidences = [
                        float(item.get('alternatives', [{}])[0].get('confidence', 0))
                        for item in items
                        if 'alternatives' in item and item['alternatives']
                    ]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                    
                    # Cleanup: Delete S3 object and transcription job
                    try:
                        self.s3_client.delete_object(Bucket=bucket_name, Key=audio_key)
                        self.transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)
                    except Exception as e:
                        logger.warning(f"Cleanup failed: {str(e)}")
                    
                    return {
                        'text': transcribed_text,
                        'language': language,
                        'confidence': avg_confidence
                    }
                
                elif status == 'FAILED':
                    failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown')
                    logger.error(f"Transcription failed: {failure_reason}")
                    raise AWSAudioClientError(f"Transcription failed: {failure_reason}")
                
                # Wait and retry
                time.sleep(2)
                wait_time += 2
            
            # Timeout
            raise AWSAudioClientError("Transcription timeout - job took too long")
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Transcribe API error: {error_code} - {error_message}")
            raise AWSAudioClientError(f"Transcribe error ({error_code}): {error_message}")
        
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise AWSAudioClientError(f"Failed to transcribe audio: {str(e)}")
    
    def text_to_speech(
        self,
        text: str,
        language: str = "hi",
        gender: str = "female"
    ) -> bytes:
        """Convert text to speech using Amazon Polly.
        
        Args:
            text: Text to convert to speech
            language: Language code (hi, en, ta, etc.)
            gender: Voice gender ('female' or 'male')
        
        Returns:
            Audio data in bytes (MP3 format)
        
        Raises:
            AWSAudioClientError: If synthesis fails
        """
        if not text or not text.strip():
            raise ValueError("text cannot be empty")
        
        try:
            # Select voice based on language and gender
            if language == 'hi' and gender == 'male':
                voice_config = self.LANGUAGE_VOICES.get('hi-male')
            else:
                voice_config = self.LANGUAGE_VOICES.get(language, self.LANGUAGE_VOICES['hi'])
            
            voice_id = voice_config['voice']
            engine = voice_config['engine']
            # Get the correct Polly LanguageCode for this voice (must match voice, not user language)
            polly_lang_code = self.POLLY_LANGUAGE_CODES.get(voice_id, 'en-US')

            logger.info(f"Synthesizing speech with voice: {voice_id} ({engine})")

            # Call Polly
            response = self.polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine,
                LanguageCode=polly_lang_code
            )
            
            # Read audio stream
            if 'AudioStream' in response:
                audio_data = response['AudioStream'].read()
                logger.info(f"Generated {len(audio_data)} bytes of audio")
                return audio_data
            else:
                raise AWSAudioClientError("No audio stream in Polly response")
        
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"Polly API error: {error_code} - {error_message}")
            raise AWSAudioClientError(f"Polly error ({error_code}): {error_message}")
        
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            raise AWSAudioClientError(f"Failed to synthesize speech: {str(e)}")
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages.
        
        Returns:
            List of language codes
        """
        return list(self.TRANSCRIBE_LANGUAGES.keys())
