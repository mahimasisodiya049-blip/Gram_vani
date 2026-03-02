"""Test script for Bhashini STT integration.

This script helps verify that the Bhashini API is working correctly
and shows the response structure for debugging.
"""

import os
from integrations import BhashiniClient
from integrations.bhashini_client import BhashiniClientError


def test_bhashini_stt():
    """Test Bhashini STT with a sample audio file."""
    
    # Get credentials from environment
    api_key = os.getenv("BHASHINI_API_KEY")
    user_id = os.getenv("BHASHINI_USER_ID")
    
    if not api_key or not user_id:
        print("❌ Error: BHASHINI_API_KEY and BHASHINI_USER_ID must be set")
        print("\nSet them in your environment:")
        print("  export BHASHINI_API_KEY='your-key'")
        print("  export BHASHINI_USER_ID='your-id'")
        return
    
    print("✅ Credentials found")
    print(f"   API Key: {api_key[:10]}...")
    print(f"   User ID: {user_id}")
    print()
    
    # Initialize client
    try:
        client = BhashiniClient(
            ulca_api_key=api_key,
            ulca_user_id=user_id
        )
        print("✅ Bhashini client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return
    
    # Test with a sample audio file
    audio_file = "sample_audio.wav"
    
    if not os.path.exists(audio_file):
        print(f"\n⚠️  Sample audio file '{audio_file}' not found")
        print("   Please provide a WAV audio file to test")
        print("\n   To test with your own audio:")
        print(f"   1. Place a WAV file named '{audio_file}' in this directory")
        print("   2. Run this script again")
        return
    
    print(f"\n📁 Reading audio file: {audio_file}")
    
    try:
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        print(f"   Audio size: {len(audio_data)} bytes")
        print()
        
        # Test STT
        print("🎤 Calling Bhashini STT API...")
        print("   Language: Hindi (hi)")
        print("   Format: WAV")
        print("   Sample Rate: 16000 Hz")
        print()
        
        result = client.speech_to_text(
            audio=audio_data,
            source_language="hi",
            audio_format="wav",
            sample_rate=16000
        )
        
        print("✅ STT Success!")
        print(f"\n📝 Transcribed Text: {result.text}")
        print(f"🌐 Language: {result.language}")
        print(f"📊 Confidence: {result.confidence}")
        
    except BhashiniClientError as e:
        print(f"\n❌ Bhashini API Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check your API credentials")
        print("   - Verify the audio file is valid WAV format")
        print("   - Ensure the audio contains clear speech")
        print("   - Check your internet connection")
    
    except FileNotFoundError:
        print(f"❌ Audio file not found: {audio_file}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 60)
    print("🎙️  Bhashini STT Test Script")
    print("=" * 60)
    print()
    
    test_bhashini_stt()
    
    print()
    print("=" * 60)
