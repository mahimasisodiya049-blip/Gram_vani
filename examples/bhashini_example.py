"""Example usage of Bhashini ULCA API client.

This script demonstrates how to use the BhashiniClient for:
1. Speech-to-Text (STT) conversion
2. Text-to-Speech (TTS) conversion
"""

import os
from integrations import BhashiniClient


def main():
    # Initialize the client with your credentials
    # Get these from environment variables or configuration
    api_key = os.getenv("BHASHINI_API_KEY", "your-api-key-here")
    user_id = os.getenv("BHASHINI_USER_ID", "your-user-id-here")
    
    client = BhashiniClient(
        ulca_api_key=api_key,
        ulca_user_id=user_id
    )
    
    # Example 1: Get supported languages
    print("Supported languages:")
    languages = client.get_supported_languages()
    print(languages)
    print()
    
    # Example 2: Speech-to-Text (STT)
    # Read audio file (you need to provide an actual audio file)
    try:
        with open("sample_audio.wav", "rb") as f:
            audio_data = f.read()
        
        print("Converting speech to text...")
        stt_result = client.speech_to_text(
            audio=audio_data,
            source_language="hi",  # Hindi
            audio_format="wav",
            sample_rate=16000
        )
        
        print(f"Transcribed text: {stt_result.text}")
        print(f"Language: {stt_result.language}")
        print(f"Confidence: {stt_result.confidence}")
        print()
    except FileNotFoundError:
        print("Audio file not found. Skipping STT example.")
        print()
    
    # Example 3: Text-to-Speech (TTS)
    print("Converting text to speech...")
    text_to_convert = "नमस्ते, यह एक परीक्षण है"  # "Hello, this is a test" in Hindi
    
    tts_result = client.text_to_speech(
        text=text_to_convert,
        target_language="hi",  # Hindi
        gender="female",
        sample_rate=16000
    )
    
    print(f"Generated audio size: {len(tts_result.audio)} bytes")
    print(f"Language: {tts_result.language}")
    print(f"Format: {tts_result.format}")
    
    # Save the generated audio
    with open("output_audio.wav", "wb") as f:
        f.write(tts_result.audio)
    print("Audio saved to output_audio.wav")


if __name__ == "__main__":
    main()
