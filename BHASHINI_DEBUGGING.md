# Bhashini STT Debugging Guide

This guide helps you troubleshoot issues with the Bhashini Speech-to-Text integration in Gram-Vani.

## Common Issues and Solutions

### Issue 1: Text Not Appearing After Speaking

**Symptoms:**
- Audio is recorded successfully
- "Process Question" button is clicked
- No transcribed text appears on screen

**Root Causes & Solutions:**

#### A. Session State Not Initialized
**Solution:** The updated `app.py` now properly initializes session state variables:
```python
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
```

#### B. Response Parsing Issues
**Solution:** The updated `bhashini_client.py` now handles multiple response structures:
- Tries `pipelineResponse[0].output[0].source`
- Falls back to `pipelineResponse[0].audio[0].source`
- Falls back to `pipelineResponse[0].source`

#### C. Empty Audio Data
**Solution:** Added validation to check if audio is empty before processing:
```python
if not audio or len(audio) == 0:
    raise ValueError("audio cannot be empty")
```

### Issue 2: Bhashini API Credentials Not Set

**Symptoms:**
- Error message: "Bhashini credentials not configured"

**Solution:**
1. Create a `.env` file in your project root:
```bash
BHASHINI_API_KEY=your-api-key-here
BHASHINI_USER_ID=your-user-id-here
```

2. Or set environment variables:
```bash
# Windows (PowerShell)
$env:BHASHINI_API_KEY="your-api-key"
$env:BHASHINI_USER_ID="your-user-id"

# Linux/Mac
export BHASHINI_API_KEY="your-api-key"
export BHASHINI_USER_ID="your-user-id"
```

3. Load environment variables in your app (add to `app.py`):
```python
from dotenv import load_dotenv
load_dotenv()
```

### Issue 3: Empty Transcription Response

**Symptoms:**
- API call succeeds but returns empty text
- Error: "Empty transcription received from Bhashini API"

**Possible Causes:**
1. Audio quality is too low
2. Background noise is too high
3. Speech is unclear or too quiet
4. Wrong language selected

**Solutions:**
- Ensure microphone is working properly
- Speak clearly and loudly
- Reduce background noise
- Verify correct language is selected
- Check audio format (should be WAV, 16kHz)

### Issue 4: API Timeout

**Symptoms:**
- Request takes too long
- Timeout error after 30 seconds

**Solutions:**
1. Check internet connection
2. Verify Bhashini service status
3. Try with shorter audio clips
4. Increase timeout in `bhashini_client.py`:
```python
response = self.session.post(
    compute_url,
    json=compute_payload,
    timeout=60  # Increase from 30 to 60 seconds
)
```

## Testing Your Integration

### Step 1: Test Bhashini Client Directly

Run the test script:
```bash
python test_bhashini_stt.py
```

This will:
- Verify your credentials
- Test the API connection
- Show the response structure
- Display any errors

### Step 2: Test with Sample Audio

1. Record a short WAV file (5-10 seconds)
2. Save it as `sample_audio.wav`
3. Run the test script
4. Check the transcribed output

### Step 3: Test in Streamlit App

1. Start the app:
```bash
streamlit run app.py
```

2. Select your language
3. Click the microphone and speak
4. Click "Process Question"
5. Check for transcribed text

## Debugging Tips

### Enable Debug Logging

Add logging to see what's happening:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In your code
logger.debug(f"Audio size: {len(audio_data)}")
logger.debug(f"API Response: {response.json()}")
```

### Inspect API Response

Add this to `bhashini_client.py` after getting the response:

```python
result = response.json()
print("DEBUG - Full API Response:")
print(json.dumps(result, indent=2))
```

### Check Session State

Add this to your Streamlit app to see session state:

```python
# Add at the bottom of app.py for debugging
if st.checkbox("Show Debug Info"):
    st.write("Session State:")
    st.json({
        "transcribed_text": st.session_state.transcribed_text,
        "audio_data_size": len(st.session_state.audio_data) if st.session_state.audio_data else 0,
        "selected_language": st.session_state.selected_language,
        "processing_error": st.session_state.processing_error
    })
```

## Response Structure Examples

### Successful Response
```json
{
  "pipelineResponse": [
    {
      "taskType": "asr",
      "output": [
        {
          "source": "नमस्ते, मैं एक सवाल पूछना चाहता हूं"
        }
      ]
    }
  ]
}
```

### Alternative Response Structure
```json
{
  "pipelineResponse": [
    {
      "audio": [
        {
          "source": "नमस्ते, मैं एक सवाल पूछना चाहता हूं"
        }
      ]
    }
  ]
}
```

## Key Changes Made

### 1. Session State Management
- Added `transcribed_text` to persist across reruns
- Added `audio_data` to store recorded audio
- Added `processing_error` to display errors

### 2. Robust Response Parsing
- Multiple fallback paths for extracting text
- Better error messages
- Validation of response structure

### 3. Error Handling
- Specific error types (BhashiniClientError, ValueError)
- User-friendly error messages
- Troubleshooting tips displayed in UI

### 4. Audio Validation
- Check for empty audio before processing
- Validate audio format and size
- Clear error messages for invalid audio

## Getting Help

If you're still experiencing issues:

1. Check the Bhashini ULCA documentation
2. Verify your API credentials are active
3. Test with the provided test script
4. Check the console for error messages
5. Enable debug logging to see detailed information

## Next Steps

Once STT is working:
1. Integrate with document retrieval (RAG)
2. Add TTS for voice responses
3. Implement error recovery
4. Add audio quality indicators
5. Support more languages
