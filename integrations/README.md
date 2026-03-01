# Bhashini ULCA API Client

This module provides a Python wrapper for the Bhashini Universal Language Contribution API (ULCA), enabling speech-to-text (STT) and text-to-speech (TTS) operations for Indian languages.

## Features

- **Speech-to-Text (STT)**: Convert audio files to text in multiple Indian languages
- **Text-to-Speech (TTS)**: Convert text to natural-sounding speech
- **Multi-language Support**: Supports 12+ Indian languages including Hindi, Tamil, Telugu, Bengali, and more
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Easy Integration**: Simple API with minimal configuration

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

You need Bhashini ULCA API credentials:

1. **API Key**: Your Bhashini ULCA API key
2. **User ID**: Your Bhashini ULCA user ID

You can obtain these by registering at the [Bhashini platform](https://bhashini.gov.in/).

## Usage

### Initialize the Client

```python
from integrations import BhashiniClient

client = BhashiniClient(
    ulca_api_key="your-api-key",
    ulca_user_id="your-user-id"
)
```

### Speech-to-Text (STT)

Convert audio to text:

```python
# Read audio file
with open("audio.wav", "rb") as f:
    audio_data = f.read()

# Convert to text
result = client.speech_to_text(
    audio=audio_data,
    source_language="hi",  # Hindi
    audio_format="wav",
    sample_rate=16000
)

print(f"Transcribed: {result.text}")
print(f"Language: {result.language}")
print(f"Confidence: {result.confidence}")
```

### Text-to-Speech (TTS)

Convert text to speech:

```python
# Convert text to speech
result = client.text_to_speech(
    text="नमस्ते, आप कैसे हैं?",
    target_language="hi",  # Hindi
    gender="female",
    sample_rate=16000
)

# Save audio file
with open("output.wav", "wb") as f:
    f.write(result.audio)

print(f"Audio format: {result.format}")
print(f"Audio size: {len(result.audio)} bytes")
```

### Get Supported Languages

```python
languages = client.get_supported_languages()
print(languages)
# Output: ['hi', 'en', 'bn', 'ta', 'te', 'mr', 'gu', 'kn', 'ml', 'pa', 'or', 'as']
```

## Supported Languages

| Code | Language   |
|------|------------|
| hi   | Hindi      |
| en   | English    |
| bn   | Bengali    |
| ta   | Tamil      |
| te   | Telugu     |
| mr   | Marathi    |
| gu   | Gujarati   |
| kn   | Kannada    |
| ml   | Malayalam  |
| pa   | Punjabi    |
| or   | Odia       |
| as   | Assamese   |

## Error Handling

The client raises `BhashiniClientError` for API-related errors:

```python
from integrations.bhashini_client import BhashiniClientError

try:
    result = client.speech_to_text(audio_data, "hi")
except BhashiniClientError as e:
    print(f"Error: {e}")
```

## API Reference

### BhashiniClient

#### `__init__(ulca_api_key: str, ulca_user_id: str)`

Initialize the client with credentials.

#### `speech_to_text(audio: bytes, source_language: str, audio_format: str = "wav", sample_rate: int = 16000) -> STTResult`

Convert speech to text.

**Parameters:**
- `audio`: Audio data in bytes
- `source_language`: Language code (e.g., 'hi', 'en')
- `audio_format`: Audio format (default: 'wav')
- `sample_rate`: Sample rate in Hz (default: 16000)

**Returns:** `STTResult` with text, language, and confidence

#### `text_to_speech(text: str, target_language: str, gender: str = "female", sample_rate: int = 16000) -> TTSResult`

Convert text to speech.

**Parameters:**
- `text`: Text to convert
- `target_language`: Language code (e.g., 'hi', 'en')
- `gender`: Voice gender ('male' or 'female')
- `sample_rate`: Sample rate in Hz (default: 16000)

**Returns:** `TTSResult` with audio bytes, language, and format

#### `get_supported_languages() -> List[str]`

Get list of supported language codes.

**Returns:** List of language codes

## Example

See `examples/bhashini_example.py` for a complete working example.

## Notes

- Audio files should be in WAV format with 16kHz sample rate for best results
- The API has rate limits; implement appropriate retry logic for production use
- Network timeouts are set to 30 seconds for compute operations and 10 seconds for configuration
- The client maintains a session for efficient connection reuse

## Troubleshooting

**Empty transcription:**
- Ensure audio quality is good
- Check that the correct language code is specified
- Verify audio format and sample rate match the parameters

**API timeout:**
- Check network connectivity
- Verify Bhashini service status
- Consider increasing timeout values for large audio files

**Authentication errors:**
- Verify your API key and user ID are correct
- Check that your credentials haven't expired
