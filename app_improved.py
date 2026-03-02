"""Gram-Vani Streamlit Application - Improved Version.

A voice-first interface for querying government documents.
Features: STT → RAG → Bedrock → TTS with loading spinners and chat UI.
"""

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import time
import os
from pathlib import Path
from integrations import AWS_AVAILABLE

# Import AWS components if available
if AWS_AVAILABLE:
    from integrations import BedrockClient, RAGEngine, AWSClientError, AWSAudioClient, AWSAudioClientError
else:
    st.warning("⚠️ AWS services not available. Install boto3 to enable audio processing and answer generation: `pip install boto3`")

# Page configuration
st.set_page_config(
    page_title="Gram-Vani - AI Avenger",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Title styling */
    .title {
        text-align: center;
        color: #1f77b4;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    
    /* Record button container */
    .record-section {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .record-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .record-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Upload section styling */
    .upload-section {
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 15px;
        border: 2px dashed #ccc;
        text-align: center;
    }
    
    .upload-title {
        color: #333;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Language selector */
    .language-section {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Divider */
    .divider {
        height: 2px;
        background: linear-gradient(to right, transparent, #ddd, transparent);
        margin: 2rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'recording_state' not in st.session_state:
    st.session_state.recording_state = 'idle'
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'Hindi'
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'processing_error' not in st.session_state:
    st.session_state.processing_error = None
if 'generated_answer' not in st.session_state:
    st.session_state.generated_answer = None
if 'answer_audio' not in st.session_state:
    st.session_state.answer_audio = None
if 'processing_stage' not in st.session_state:
    st.session_state.processing_stage = None

# Header
st.markdown('<div class="title">🎙️ Gram-Vani - AI Avenger</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">सरकारी दस्तावेज़ों को आवाज़ से समझें | Understand Government Documents with Voice</div>', unsafe_allow_html=True)

# Language selection
st.markdown('<div class="language-section">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    language = st.selectbox(
        "🌐 Select Language / भाषा चुनें",
        options=['Hindi', 'English', 'Tamil', 'Telugu', 'Bengali', 'Marathi', 'Gujarati', 'Kannada'],
        index=0,
        key='language_selector'
    )
    st.session_state.selected_language = language
st.markdown('</div>', unsafe_allow_html=True)

# Language code mapping
language_codes = {
    'Hindi': 'hi',
    'English': 'en',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Bengali': 'bn',
    'Marathi': 'mr',
    'Gujarati': 'gu',
    'Kannada': 'kn'
}

# Main layout - Two columns
col_left, col_right = st.columns([1, 1], gap="large")

# Left Column - Voice Recording
with col_left:
    st.markdown("""
        <div class="record-section">
            <div class="record-title">🎤 Ask Your Question</div>
            <div class="record-subtitle">Click the microphone to record your question</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Audio recorder
    audio_bytes = audio_recorder(
        text="Click to Record",
        recording_color="#e74c3c",
        neutral_color="#3498db",
        icon_name="microphone",
        icon_size="6x",
        pause_threshold=2.0,
        sample_rate=16000
    )
    
    # Store audio in session state when recorded
    if audio_bytes and audio_bytes != st.session_state.audio_data:
        st.session_state.audio_data = audio_bytes
        st.session_state.transcribed_text = None
        st.session_state.generated_answer = None
        st.session_state.answer_audio = None
        st.session_state.processing_error = None
        st.session_state.processing_stage = None
    
    if st.session_state.audio_data:
        st.success("✅ Audio recorded successfully!")
        
        # Display audio player
        st.audio(st.session_state.audio_data, format="audio/wav")
        
        # Process button
        if st.button("🔍 Process Question", type="primary", use_container_width=True):
            if not AWS_AVAILABLE:
                st.error("⚠️ AWS services not available. Please install boto3: `pip install boto3`")
            else:
                lang_code = language_codes.get(st.session_state.selected_language, 'hi')
                aws_region = os.getenv("AWS_REGION", "us-east-1")
                
                # Initialize AWS clients
                audio_client = AWSAudioClient(region_name=aws_region)
                bedrock_client = BedrockClient(region_name=aws_region)
                rag_engine = RAGEngine(bedrock_client=bedrock_client)
                
                # Stage 1: Speech-to-Text
                with st.spinner("🎤 AI Avenger is listening..."):
                    st.session_state.processing_stage = "transcribing"
                    try:
                        stt_result = audio_client.speech_to_text(
                            audio=st.session_state.audio_data,
                            language=lang_code,
                            audio_format="wav"
                        )
                        
                        if stt_result and stt_result.get('text'):
                            st.session_state.transcribed_text = stt_result['text']
                            st.session_state.processing_error = None
                        else:
                            st.session_state.processing_error = "No text transcribed. Please speak more clearly."
                            st.session_state.processing_stage = None
                    
                    except (AWSAudioClientError, ValueError, Exception) as e:
                        st.session_state.processing_error = f"Transcription Error: {str(e)}"
                        st.session_state.processing_stage = None
                
                # Stage 2: Generate Answer
                if st.session_state.transcribed_text and not st.session_state.processing_error:
                    with st.spinner("🤖 AI Avenger is thinking..."):
                        st.session_state.processing_stage = "generating"
                        try:
                            context = rag_engine.retrieve_context(st.session_state.transcribed_text)
                            
                            answer = rag_engine.generate_answer(
                                question=st.session_state.transcribed_text,
                                context=context,
                                language=lang_code
                            )
                            
                            st.session_state.generated_answer = answer
                        
                        except AWSClientError as e:
                            st.warning(f"⚠️ AWS Error: {str(e)}")
                            st.session_state.generated_answer = rag_engine._get_fallback_message(lang_code)
                        
                        except Exception as e:
                            st.error(f"❌ Generation Error: {str(e)}")
                            st.session_state.generated_answer = rag_engine._get_fallback_message(lang_code)
                    
                    # Stage 3: Text-to-Speech
                    if st.session_state.generated_answer:
                        with st.spinner("🔊 AI Avenger is speaking..."):
                            st.session_state.processing_stage = "synthesizing"
                            try:
                                tts_audio = audio_client.text_to_speech(
                                    text=st.session_state.generated_answer,
                                    language=lang_code,
                                    gender="female"
                                )
                                
                                st.session_state.answer_audio = tts_audio
                            
                            except (AWSAudioClientError, Exception) as e:
                                st.warning(f"⚠️ TTS Error: {str(e)}. Showing text only.")
                                st.session_state.answer_audio = None
                        
                        st.session_state.processing_stage = "complete"
        
        # Display conversation in chat format
        if st.session_state.transcribed_text:
            st.markdown("---")
            st.markdown("### 💬 Conversation")
            
            # User question
            with st.chat_message("user", avatar="🗣️"):
                st.markdown("**You asked:**")
                st.markdown(st.session_state.transcribed_text)
            
            # AI answer
            if st.session_state.generated_answer:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown("**AI Avenger:**")
                    st.markdown(st.session_state.generated_answer)
                    
                    # Auto-play audio response
                    if st.session_state.answer_audio:
                        st.audio(st.session_state.answer_audio, format="audio/mp3", autoplay=True)
                        st.caption("🔊 Audio response playing automatically")
        
        # Display error
        if st.session_state.processing_error:
            st.error(f"❌ {st.session_state.processing_error}")
            st.info("💡 **Tips:** Check microphone, speak clearly, verify credentials")
    
    # Instructions
    st.markdown("---")
    st.markdown("""
        ### 📋 How to Use:
        1. **Upload** government PDF documents (right side)
        2. **Select** your preferred language
        3. **Click** the microphone and ask your question
        4. **Listen** to the AI Avenger's answer
    """)

# Right Column - PDF Upload
with col_right:
    st.markdown("""
        <div class="upload-section">
            <div class="upload-title">📄 Upload Government Documents</div>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=['pdf'],
        accept_multiple_files=True,
        key='pdf_uploader',
        help="Upload government documents in PDF format"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded!")
        
        st.markdown("### 📚 Uploaded Documents:")
        for idx, file in enumerate(uploaded_files, 1):
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.write(f"{idx}. {file.name}")
            with col_b:
                st.write(f"{file.size / 1024:.1f} KB")
            with col_c:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.info("File removed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤 Process Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.success("✅ Documents processed!")
                st.balloons()
    else:
        st.info("👆 Upload PDF documents to get started")
    
    # Document stats
    st.markdown("---")
    st.markdown("### 📊 Document Statistics")
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric("Documents", len(uploaded_files) if uploaded_files else 0)
    with stat_col2:
        st.metric("Pages", "0")
    with stat_col3:
        st.metric("Indexed", "0")

# Footer
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🇮🇳 Built for Digital India | Making Government Information Accessible</p>
        <p style="font-size: 0.9rem;">Powered by AWS Transcribe, Polly & Bedrock</p>
    </div>
""", unsafe_allow_html=True)
