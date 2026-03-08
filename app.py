import json
import streamlit as st
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text
import pymupdf

genai.configure(api_key=st.secrets["GRAMVANI_GEMINI_KEY"])

st.set_page_config(
    page_title="Gram-Vani | AI Avenger",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.brand-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    text-align: center;
}
.brand-header h1 { font-size: 2.4rem; margin: 0; font-weight: 700; }
.brand-header p  { margin: 0.3rem 0 0; color: #a8c8ff; font-size: 1rem; }
.brand-badge {
    display: inline-block;
    background: #e63946;
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    margin-top: 0.5rem;
    letter-spacing: 0.05em;
}
.answer-box {
    background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
    border-left: 5px solid #43a047;
    border-radius: 10px;
    padding: 1.3rem 1.6rem;
    margin-top: 1rem;
    font-size: 1.05rem;
    line-height: 1.8;
    color: #1b5e20;
}
.question-box {
    background: #ede7f6;
    border-left: 5px solid #7e57c2;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    color: #311b92;
    font-style: italic;
}
.source-box {
    background: #fff8e1;
    border-left: 4px solid #ffa000;
    border-radius: 8px;
    padding: 0.7rem 1.2rem;
    margin-top: 0.8rem;
    font-size: 0.85rem;
    color: #5d4037;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand-header">
  <h1>🎙️ Gram-Vani</h1>
  <p>सरकारी योजनाओं की जानकारी — आपकी भाषा में</p>
  <span class="brand-badge">⚡ AI Avenger &nbsp;|&nbsp; AI for Bharat Hackathon</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    lang_display = st.selectbox(
        "🌐 Language / भाषा",
        options=["Hindi", "Marathi", "English"],
        index=0,
    )
    LANG_MAP = {
        "Hindi":   {"web_code": "hi-IN", "short": "hi",  "label": "हिंदी"},
        "Marathi": {"web_code": "mr-IN", "short": "mr",  "label": "मराठी"},
        "English": {"web_code": "en-US", "short": "en",  "label": "English"},
    }
    lang = LANG_MAP[lang_display]

    st.markdown("---")
    st.markdown("**🏗️ Architecture**")
    st.markdown("""
- 🎤 **Bhashini** Web STT
- 📄 **PyMuPDF** PDF parser
- 🤖 **Gemini 1.5 Flash** RAG
- ☁️ AWS S3 / Lambda *(planned)*
    """)
    st.markdown("---")
    st.markdown("**📋 How to use:**")
    st.markdown("1. Upload a govt PDF")
    st.markdown("2. Speak or type your question")
    st.markdown("3. Get answer in your language")

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

st.markdown("### 📄 Step 1: Upload a Government Scheme PDF")
uploaded_file = st.file_uploader(
    "Upload a PDF (PM-Kisan, APY, PMAY, etc.)",
    type="pdf",
    help="The text from this document will be used as context for your questions.",
)

def extract_text_from_pdf(file) -> str:
    doc = pymupdf.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

if uploaded_file:
    if uploaded_file.name != st.session_state.pdf_name:
        with st.spinner("📖 Reading document…"):
            st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
            st.session_state.pdf_name = uploaded_file.name
            st.session_state.last_question = ""
            st.session_state.last_answer = ""
        st.success(f"✅ **{uploaded_file.name}** loaded — {len(st.session_state.pdf_text):,} characters extracted.")
    else:
        st.success(f"✅ **{uploaded_file.name}** ready.")
else:
    st.info("👆 Upload a PDF to get started. You can still ask general questions without one.")

SYSTEM_PROMPTS = {
    "hi": (
        "आप 'Gram-Vani' हैं — AI Avenger टीम द्वारा बनाया गया एक सहायक, जो ग्रामीण "
        "भारतीय नागरिकों को सरकारी योजनाओं को समझने में मदद करता है। "
        "दिए गए संदर्भ के आधार पर सरल और स्पष्ट हिंदी में उत्तर दें। "
        "यदि उत्तर संदर्भ में नहीं है, तो विनम्रता से बताएं।"
    ),
    "mr": (
        "तुम्ही 'Gram-Vani' आहात — AI Avenger टीमने तयार केलेले सहाय्यक, जे ग्रामीण "
        "भारतीय नागरिकांना सरकारी योजना समजण्यास मदत करते. "
        "दिलेल्या संदर्भावर आधारित सोप्या मराठीत उत्तर द्या. "
        "संदर्भात उत्तर नसल्यास, नम्रपणे सांगा."
    ),
    "en": (
        "You are 'Gram-Vani', a helpful assistant by Team AI Avenger, designed to help "
        "rural Indian citizens understand government schemes. Answer clearly and simply "
        "based on the provided context. If the answer is not in the context, say so politely."
    ),
}

def ask_gemini(question: str, context: str, lang_short: str) -> str:
    system = SYSTEM_PROMPTS.get(lang_short, SYSTEM_PROMPTS["en"])
    if context.strip():
        prompt = (
            f"{system}\n\n"
            f"--- Document Context ---\n{context[:12000]}\n--- End Context ---\n\n"
            f"Question: {question}\n\n"
            f"Respond ONLY in {lang_display}."
        )
    else:
        prompt = (
            f"{system}\n\n"
            f"No document was uploaded. Answer from general knowledge.\n\n"
            f"Question: {question}\n\n"
            f"Respond ONLY in {lang_display}."
        )
    
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
    except Exception:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        
    return response.text

st.markdown("---")
st.markdown(f"### 🎤 Step 2: Ask Your Question in **{lang['label']}**")

col_voice, col_type = st.columns([1, 1], gap="medium")

with col_voice:
    st.markdown("**🎙️ Speak (via Bhashini Web STT):**")
    try:
        from streamlit_mic_recorder import speech_to_text as _stt
        spoken = _stt(
            language=lang["web_code"],
            start_prompt="⏺️ Start Speaking",
            stop_prompt="⏹️ Stop & Process",
            just_once=True,
            use_container_width=True,
            key=f"stt_{lang_display}",
        )
    except ImportError:
        st.warning("`streamlit-mic-recorder` not found. Run `pip install streamlit-mic-recorder`.")
        spoken = None
    st.caption("Works best in Chrome / Edge. Allow microphone when prompted.")

with col_type:
    st.markdown("**⌨️ Or Type your question:**")
    typed = st.text_area(
        "Type here…",
        placeholder="e.g. PM Kisan में कितनी राशि मिलती है?",
        height=120,
        label_visibility="collapsed",
    )
    submit = st.button("🔍 Get Answer", use_container_width=True, type="primary")

question = ""
if spoken and spoken.strip():
    question = spoken.strip()
elif submit and typed.strip():
    question = typed.strip()

if question and question != st.session_state.last_question:
    st.session_state.last_question = question
    st.session_state.last_answer = ""

    st.markdown(
        f'<div class="question-box">🗣️ <strong>You asked:</strong> {question}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("🤖 Gram-Vani is thinking…"):
        try:
            answer = ask_gemini(question, st.session_state.pdf_text, lang["short"])
            st.session_state.last_answer = answer
        except Exception as e:
            err = str(e)
            if "API_KEY" in err.upper() or "api key" in err.lower():
                st.error("🔑 **API Key Error** — Open `.streamlit/secrets.toml` and set `GRAMVANI_GEMINI_KEY`.")
            else:
                st.error(f"❌ Gemini Error: {err}")
            st.stop()

elif question and question == st.session_state.last_question:
    st.markdown(
        f'<div class="question-box">🗣️ <strong>You asked:</strong> {question}</div>',
        unsafe_allow_html=True,
    )

if st.session_state.last_answer:
    st.markdown(
        f'<div class="answer-box">📢 <strong>Gram-Vani responds:</strong><br><br>'
        f'{st.session_state.last_answer}</div>',
        unsafe_allow_html=True,
    )
    if st.session_state.pdf_name:
        st.markdown(
            f'<div class="source-box">📄 Source document: <strong>{st.session_state.pdf_name}</strong></div>',
            unsafe_allow_html=True,
        )
    st.markdown("")
    if st.button("🔄 Ask another question", use_container_width=True):
        st.session_state.last_question = ""
        st.session_state.last_answer = ""
        st.rerun()

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.82rem'>"
    "🇮🇳 <strong>Gram-Vani</strong> &nbsp;|&nbsp; Team AI Avenger &nbsp;|&nbsp; "
    "AI for Bharat Hackathon &nbsp;|&nbsp; "
    "Hybrid RAG: Bhashini STT × Gemini 1.5 Flash × PyMuPDF"
    "</div>",
    unsafe_allow_html=True,
)
