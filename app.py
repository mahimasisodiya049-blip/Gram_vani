"""Gram-Vani Streamlit Application.

A voice-first interface for querying government documents.
Users can upload PDFs and ask questions via voice.
"""

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import time
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Gram-Vani",
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
    
    /* Status messages */
    .status-success {
        padding: 1rem;
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        color: #155724;
        margin: 1rem 0;
    }
    
    .status-info {
        padding: 1rem;
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        color: #0c5460;
        margin: 1rem 0;
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

# Header
st.markdown('<div class="title">🎙️ Gram-Vani</div>', unsafe_allow_html=True)
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
    
    if audio_bytes:
        st.success("✅ Audio recorded successfully!")
        
        # Display audio player
        st.audio(audio_bytes, format="audio/wav")
        
        # Process button
        if st.button("🔍 Process Question", type="primary", use_container_width=True):
            with st.spinner("Processing your question..."):
                # Simulate processing
                time.sleep(1)
                st.info("🎯 **Transcribed Question:** आपका सवाल यहाँ दिखेगा")
                time.sleep(1)
                st.markdown("""
                    <div class="status-info">
                        <strong>📝 Answer:</strong><br>
                        Your answer will appear here based on the uploaded documents.
                    </div>
                """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("---")
    st.markdown("""
        ### 📋 How to Use:
        1. **Upload** government PDF documents (right side)
        2. **Select** your preferred language
        3. **Click** the microphone and ask your question
        4. **Listen** to the simplified answer
    """)

# Right Column - PDF Upload
with col_right:
    st.markdown("""
        <div class="upload-section">
            <div class="upload-title">📄 Upload Government Documents</div>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Drop PDF files here or click to browse",
        type=['pdf'],
        accept_multiple_files=True,
        key='pdf_uploader',
        help="Upload government documents in PDF format"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Display uploaded files
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
        
        # Process documents button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📤 Process Documents", type="primary", use_container_width=True):
            with st.spinner("Processing documents..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                
                st.success("✅ Documents processed and indexed successfully!")
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
        <p style="font-size: 0.9rem;">Powered by Bhashini ULCA & AWS Bedrock</p>
    </div>
""", unsafe_allow_html=True)
