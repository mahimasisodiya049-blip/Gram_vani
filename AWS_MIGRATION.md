# AWS Audio Services Migration

## Overview

This document describes the migration from Bhashini ULCA API to AWS Transcribe and Polly for audio processing in Gram-Vani.

## Reason for Migration

The Bhashini API was experiencing downtime on Streamlit Cloud, causing the application to fail. AWS services provide:
- Higher reliability and uptime
- Better integration with existing AWS infrastructure (Bedrock)
- Consistent authentication mechanism
- Better performance for production workloads

## Changes Made

### 1. New AWS Audio Client

**File**: `integrations/aws_audio_client.py`

Created a new client that provides:
- **Speech-to-Text (STT)**: Using Amazon Transcribe
- **Text-to-Speech (TTS)**: Using Amazon Polly

#### Supported Languages

| Language | Transcribe Code | Polly Voice | Gender |
|----------|----------------|-------------|---------|
| Hindi | hi-IN | Aditi | Female |
| Hindi | hi-IN | Madhav | Male |
| English | en-US | Joanna | Female |
| Tamil | ta-IN | Joanna (fallback) | Female |
| Telugu | te-IN | Joanna (fallback) | Female |
| Bengali | bn-IN | Joanna (fallback) | Female |

#### Key Features

- **Automatic S3 bucket creation**: Creates `gram-vani-transcribe-{region}` bucket if needed
- **Async transcription**: Polls Transcribe job status until complete
- **Confidence scores**: Returns average confidence from transcription
- **Automatic cleanup**: Deletes S3 objects and transcription jobs after processing
- **Error handling**: Comprehensive error messages for debugging

### 2. Updated Integration Layer

**File**: `integrations/__init__.py`

Added exports:
```python
from .aws_audio_client import AWSAudioClient, AWSAudioClientError
```

### 3. Updated Applications

#### app.py

**Changes**:
- Removed Bhashini client imports
- Added AWS audio client initialization
- Updated STT call to use `audio_client.speech_to_text()`
- Removed Bhashini credential checks
- Updated footer to mention AWS services

**Before**:
```python
from integrations import BhashiniClient
client = BhashiniClient(ulca_api_key=api_key, ulca_user_id=user_id)
result = client.speech_to_text(audio=audio_data, source_language=lang_code)
```

**After**:
```python
from integrations import AWSAudioClient
audio_client = AWSAudioClient(region_name=aws_region)
result = audio_client.speech_to_text(audio=audio_data, language=lang_code)
```

#### app_improved.py

**Changes**:
- Complete end-to-end flow: Audio → Transcribe → Bedrock → Polly → Audio
- Updated all three processing stages to use AWS services
- Changed audio format from WAV to MP3 for Polly output
- Maintained loading spinners and chat UI

**Data Flow**:
1. **Stage 1 - STT**: `AWSAudioClient.speech_to_text()` → Amazon Transcribe
2. **Stage 2 - RAG**: `RAGEngine.generate_answer()` → Amazon Bedrock
3. **Stage 3 - TTS**: `AWSAudioClient.text_to_speech()` → Amazon Polly

### 4. Updated Documentation

#### SETUP_CREDENTIALS.md

**Changes**:
- Removed Bhashini credential instructions
- Added AWS Transcribe and Polly IAM permissions
- Updated troubleshooting section
- Added S3 bucket permissions
- Simplified credential setup (AWS only)

**New IAM Permissions Required**:
```json
{
    "Sid": "TranscribeAccess",
    "Effect": "Allow",
    "Action": [
        "transcribe:StartTranscriptionJob",
        "transcribe:GetTranscriptionJob",
        "transcribe:DeleteTranscriptionJob"
    ],
    "Resource": "*"
},
{
    "Sid": "PollyAccess",
    "Effect": "Allow",
    "Action": [
        "polly:SynthesizeSpeech"
    ],
    "Resource": "*"
},
{
    "Sid": "S3Access",
    "Effect": "Allow",
    "Action": [
        "s3:CreateBucket",
        "s3:HeadBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
    ],
    "Resource": [
        "arn:aws:s3:::gram-vani-transcribe-*",
        "arn:aws:s3:::gram-vani-transcribe-*/*"
    ]
}
```

## Technical Details

### Amazon Transcribe Workflow

1. **Upload audio to S3**: Audio bytes → S3 bucket
2. **Start transcription job**: Submit job with language code
3. **Poll for completion**: Check status every 2 seconds (max 60 seconds)
4. **Download transcript**: Fetch JSON from transcript URI
5. **Extract text and confidence**: Parse results
6. **Cleanup**: Delete S3 object and transcription job

### Amazon Polly Workflow

1. **Select voice**: Based on language and gender preference
2. **Synthesize speech**: Call Polly with text and voice parameters
3. **Return audio**: MP3 format audio bytes
4. **Auto-play**: Streamlit plays audio automatically

### Error Handling

Both services include comprehensive error handling:

```python
try:
    result = audio_client.speech_to_text(audio=audio_data, language='hi')
except AWSAudioClientError as e:
    # Handle AWS-specific errors (permissions, service issues)
    st.error(f"AWS Audio Error: {str(e)}")
except ValueError as e:
    # Handle validation errors (empty audio, invalid format)
    st.error(f"Validation Error: {str(e)}")
except Exception as e:
    # Handle unexpected errors
    st.error(f"Unexpected Error: {str(e)}")
```

## Migration Checklist

For users migrating from Bhashini to AWS:

- [x] Create `AWSAudioClient` class
- [x] Implement Transcribe STT with S3 workflow
- [x] Implement Polly TTS with Indian voices
- [x] Update `integrations/__init__.py` exports
- [x] Update `app.py` to use AWS audio client
- [x] Update `app_improved.py` to use AWS audio client
- [x] Update `SETUP_CREDENTIALS.md` documentation
- [x] Remove Bhashini credential requirements
- [x] Add IAM permission documentation
- [x] Test complete audio flow
- [ ] Deploy to Streamlit Cloud
- [ ] Update environment variables/secrets
- [ ] Test in production

## Deployment Steps

### For Streamlit Cloud

1. **Update Secrets** (Settings → Secrets):
```toml
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
AWS_REGION = "us-east-1"
```

2. **Remove Old Secrets**:
   - Delete `BHASHINI_API_KEY`
   - Delete `BHASHINI_USER_ID`

3. **Update IAM Permissions**:
   - Add Transcribe permissions
   - Add Polly permissions
   - Add S3 permissions for `gram-vani-transcribe-*` buckets

4. **Deploy**:
   - Push changes to GitHub
   - Streamlit Cloud will auto-deploy
   - Test audio recording and playback

### For Local Development

1. **Update `.env` file**:
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

2. **Install dependencies**:
```bash
pip install boto3
```

3. **Run application**:
```bash
streamlit run app_improved.py
```

## Performance Considerations

### Transcribe
- **Latency**: 5-15 seconds for typical voice queries
- **Cost**: $0.024 per minute (first 250 million minutes free tier)
- **Accuracy**: High accuracy for Indian languages

### Polly
- **Latency**: < 1 second for typical responses
- **Cost**: $4.00 per 1 million characters (first 5 million free tier)
- **Quality**: Neural voices provide natural-sounding speech

### S3
- **Storage**: Temporary (files deleted after transcription)
- **Cost**: Minimal (files stored < 1 minute)
- **Bucket**: Auto-created per region

## Backward Compatibility

The Bhashini client (`integrations/bhashini_client.py`) is still available but not used by default. To switch back:

1. Revert imports in `app.py` and `app_improved.py`
2. Add Bhashini credentials to environment
3. Change client initialization

However, this is not recommended due to reliability issues.

## Testing

### Manual Testing

1. **Record audio**: Click microphone, speak in Hindi
2. **Verify transcription**: Check text appears correctly
3. **Verify answer**: Check Bedrock generates response
4. **Verify TTS**: Check audio plays automatically

### Expected Behavior

- Loading spinners show progress
- Transcribed text displays in chat
- Answer appears in assistant message
- Audio plays automatically (MP3 format)
- No credential errors

## Troubleshooting

### Common Issues

1. **"S3 upload failed"**
   - Check S3 permissions in IAM
   - Verify bucket name doesn't conflict
   - Check region supports S3

2. **"Transcription timeout"**
   - Audio file may be too long (> 60 seconds)
   - Check Transcribe service status
   - Verify audio format is supported

3. **"Polly error"**
   - Check Polly permissions in IAM
   - Verify language is supported
   - Ensure text is not empty

## Future Enhancements

Potential improvements:
- [ ] Support for more Indian languages (Marathi, Gujarati, Kannada)
- [ ] Streaming transcription for real-time feedback
- [ ] Voice selection UI (male/female)
- [ ] Audio quality settings
- [ ] Caching for repeated queries
- [ ] Cost optimization (reuse S3 bucket, batch processing)

## References

- [AWS Transcribe Documentation](https://docs.aws.amazon.com/transcribe/)
- [AWS Polly Documentation](https://docs.aws.amazon.com/polly/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Streamlit Audio Components](https://docs.streamlit.io/library/api-reference/media)

## Conclusion

The migration to AWS audio services provides a more reliable and scalable solution for Gram-Vani. All audio processing now uses AWS infrastructure, ensuring consistent performance and easier maintenance.
