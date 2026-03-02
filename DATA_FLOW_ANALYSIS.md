# Gram-Vani Data Flow Analysis

## Complete Data Flow: Audio Input → Text Output

This document analyzes the complete data flow from audio input to final text/audio output in the Gram-Vani application.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: AUDIO CAPTURE                                          │
│  Component: audio_recorder_streamlit                             │
│  Input: User voice                                               │
│  Output: audio_bytes (WAV format, 16kHz)                         │
│  Storage: st.session_state.audio_data                            │
│  UI: "✅ Audio recorded successfully!"                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: SPEECH-TO-TEXT (STT)                                   │
│  Component: BhashiniClient.speech_to_text()                      │
│  Input: audio_bytes, language_code                               │
│  Processing:                                                      │
│    1. Encode audio to base64                                     │
│    2. Get pipeline config from Bhashini                          │
│    3. Call ULCA STT API                                          │
│    4. Parse response: pipelineResponse[0].output[0].source       │
│  Output: STTResult(text, language, confidence)                   │
│  Storage: st.session_state.transcribed_text                      │
│  UI: with st.spinner("🎤 AI Avenger is listening...")            │
│  Display: st.chat_message("user") with transcribed text          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: CONTEXT RETRIEVAL (RAG)                                │
│  Component: RAGEngine.retrieve_context()                         │
│  Input: transcribed_text                                         │
│  Processing:                                                      │
│    1. Generate query embedding (future)                          │
│    2. Search vector database (future)                            │
│    3. Retrieve top-k relevant chunks (future)                    │
│  Output: context_string or None                                  │
│  Current: Returns None (placeholder)                             │
│  Fallback: Continues without context                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: ANSWER GENERATION                                      │
│  Component: RAGEngine.generate_answer()                          │
│  Input: question, context, language                              │
│  Processing:                                                      │
│    1. Build system prompt (language-specific)                    │
│    2. Build user prompt (with/without context)                   │
│    3. Call BedrockClient.generate_text()                         │
│       - Model: Claude 3.5 Sonnet                                 │
│       - Payload: anthropic_version, messages, system             │
│    4. Parse response: content[0].text                            │
│  Output: answer_text                                             │
│  Storage: st.session_state.generated_answer                      │
│  UI: with st.spinner("🤖 AI Avenger is thinking...")             │
│  Display: st.chat_message("assistant") with answer               │
│  Fallback: Multilingual fallback message on error                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5: TEXT-TO-SPEECH (TTS)                                   │
│  Component: BhashiniClient.text_to_speech()                      │
│  Input: answer_text, language_code                               │
│  Processing:                                                      │
│    1. Get pipeline config from Bhashini                          │
│    2. Call ULCA TTS API                                          │
│    3. Parse response: pipelineResponse[0].audio[0].audioContent  │
│    4. Decode base64 to audio bytes                               │
│  Output: TTSResult(audio, language, format)                      │
│  Storage: st.session_state.answer_audio                          │
│  UI: with st.spinner("🔊 AI Avenger is speaking...")             │
│  Display: st.audio(autoplay=True) - triggers automatically       │
│  Fallback: Text-only display if TTS fails                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     FINAL OUTPUT                                  │
│  - Transcribed question in chat bubble                           │
│  - Generated answer in chat bubble                               │
│  - Audio response (auto-playing)                                 │
│  - All persisted in session state                                │
└─────────────────────────────────────────────────────────────────┘
```

## Session State Management

### State Variables

| Variable | Type | Purpose | Lifecycle |
|----------|------|---------|-----------|
| `audio_data` | bytes | Stores recorded audio | Reset on new recording |
| `transcribed_text` | str | STT output | Reset on new recording |
| `generated_answer` | str | Bedrock output | Reset on new recording |
| `answer_audio` | bytes | TTS output | Reset on new recording |
| `processing_error` | str | Error messages | Reset on new recording |
| `processing_stage` | str | Current stage | Tracks progress |

### State Flow

```python
# New recording detected
if audio_bytes != st.session_state.audio_data:
    st.session_state.audio_data = audio_bytes
    st.session_state.transcribed_text = None      # Clear previous
    st.session_state.generated_answer = None      # Clear previous
    st.session_state.answer_audio = None          # Clear previous
    st.session_state.processing_error = None      # Clear previous
    st.session_state.processing_stage = None      # Clear previous

# Processing stages
st.session_state.processing_stage = "transcribing"  # Stage 1
st.session_state.processing_stage = "generating"    # Stage 2
st.session_state.processing_stage = "synthesizing"  # Stage 3
st.session_state.processing_stage = "complete"      # Done
```

## Loading Spinners

### Implementation

Each processing stage has a dedicated spinner with descriptive text:

```python
# Stage 1: STT
with st.spinner("🎤 AI Avenger is listening..."):
    # Transcription code
    pass

# Stage 2: RAG + Bedrock
with st.spinner("🤖 AI Avenger is thinking..."):
    # Answer generation code
    pass

# Stage 3: TTS
with st.spinner("🔊 AI Avenger is speaking..."):
    # Audio synthesis code
    pass
```

### User Experience

- **Visual Feedback**: Spinner shows processing is happening
- **Descriptive Text**: User knows what stage is running
- **Sequential**: Spinners appear one after another
- **Non-blocking**: UI remains responsive

## Chat Message Containers

### Implementation

```python
# User message
with st.chat_message("user", avatar="🗣️"):
    st.markdown("**You asked:**")
    st.markdown(st.session_state.transcribed_text)

# Assistant message
with st.chat_message("assistant", avatar="🤖"):
    st.markdown("**AI Avenger:**")
    st.markdown(st.session_state.generated_answer)
    
    # Auto-play audio
    if st.session_state.answer_audio:
        st.audio(st.session_state.answer_audio, format="audio/wav", autoplay=True)
        st.caption("🔊 Audio response playing automatically")
```

### Benefits

- **Clean UI**: Chat-like interface familiar to users
- **Visual Hierarchy**: Clear distinction between user and AI
- **Contextual**: Shows conversation flow
- **Persistent**: Remains visible across reruns

## Automatic Audio Playback

### Implementation

```python
st.audio(
    st.session_state.answer_audio,
    format="audio/wav",
    autoplay=True  # ← Triggers automatic playback
)
```

### Behavior

1. Audio is generated in Stage 3 (TTS)
2. Stored in `st.session_state.answer_audio`
3. Displayed with `autoplay=True`
4. Browser automatically plays audio
5. User hears response without clicking

### Fallback

If TTS fails:
```python
except BhashiniClientError as e:
    st.warning(f"⚠️ TTS Error: {str(e)}. Showing text only.")
    st.session_state.answer_audio = None
```

Text answer still displayed, just no audio.

## Error Handling Flow

```
Try:
    Execute stage
    ↓
    Success → Store result in session state
    ↓
    Continue to next stage

Catch Error:
    ↓
    Log error
    ↓
    Display user-friendly message
    ↓
    Use fallback (if available)
    ↓
    Stop processing or continue with degraded functionality
```

### Error Types

1. **STT Errors**: Show error, stop processing
2. **Bedrock Errors**: Show warning, use fallback message
3. **TTS Errors**: Show warning, display text only
4. **Network Errors**: Show error with retry suggestion

## Performance Considerations

### Latency Breakdown

| Stage | Typical Time | Optimization |
|-------|--------------|--------------|
| Audio Capture | Instant | N/A |
| STT (Bhashini) | 2-5 seconds | Use faster models |
| Context Retrieval | < 1 second | Vector search optimization |
| Bedrock Generation | 3-8 seconds | Reduce max_tokens |
| TTS (Bhashini) | 2-4 seconds | Cache common phrases |
| **Total** | **7-18 seconds** | Parallel processing |

### Optimization Strategies

1. **Parallel Processing**: Run independent operations concurrently
2. **Caching**: Cache embeddings and common responses
3. **Streaming**: Stream Bedrock responses (future)
4. **Preloading**: Initialize clients once, reuse
5. **Compression**: Compress audio for faster transfer

## Data Persistence

### What Persists

✅ Transcribed text (across reruns)
✅ Generated answer (across reruns)
✅ Answer audio (across reruns)
✅ Error messages (across reruns)

### What Resets

❌ Audio data (on new recording)
❌ Processing stage (on new recording)
❌ All outputs (on new recording)

## Testing the Flow

### Manual Test

1. Start app: `streamlit run app_improved.py`
2. Select language
3. Click microphone, speak
4. Click "Process Question"
5. Observe spinners:
   - "AI Avenger is listening..."
   - "AI Avenger is thinking..."
   - "AI Avenger is speaking..."
6. See chat messages appear
7. Hear audio auto-play

### Debug Mode

Add to app:
```python
if st.checkbox("Show Debug Info"):
    st.json({
        "audio_size": len(st.session_state.audio_data) if st.session_state.audio_data else 0,
        "transcribed_text": st.session_state.transcribed_text,
        "answer_length": len(st.session_state.generated_answer) if st.session_state.generated_answer else 0,
        "audio_response_size": len(st.session_state.answer_audio) if st.session_state.answer_audio else 0,
        "processing_stage": st.session_state.processing_stage,
        "error": st.session_state.processing_error
    })
```

## Key Improvements

### Before
- ❌ Generic spinner text
- ❌ Plain text display
- ❌ Manual audio playback
- ❌ No stage tracking
- ❌ Unclear processing status

### After
- ✅ Descriptive spinners ("AI Avenger is thinking...")
- ✅ Clean chat message containers
- ✅ Automatic audio playback
- ✅ Stage tracking in session state
- ✅ Clear visual feedback at each stage

## Files

- **Main App**: `app_improved.py`
- **Original**: `app.py` (backup)
- **This Doc**: `DATA_FLOW_ANALYSIS.md`

## Usage

Replace the old app:
```bash
mv app.py app_old.py
mv app_improved.py app.py
streamlit run app.py
```

Or run directly:
```bash
streamlit run app_improved.py
```
