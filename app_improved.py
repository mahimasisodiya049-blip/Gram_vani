"""Gram-Vani — Emergency Prototype
Browser-native STT → Bedrock Claude 3.5 Sonnet → Text answer
No Bhashini keys needed. No WebSocket. Works out of the box.
"""

import json
import streamlit as st
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Gram-Vani | AI Avenger",
    page_icon="🎙️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Minimal, clean CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.hero h1 { font-size: 2.6rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0.2rem; }
.hero p  { color: #555; font-size: 1.05rem; }
.answer-box {
    background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
    border-left: 5px solid #43a047;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #1b5e20;
}
.question-box {
    background: #ede7f6;
    border-left: 5px solid #7e57c2;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-top: 1rem;
    color: #311b92;
    font-style: italic;
}
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar — Language selector ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/320px-Flag_of_India.svg.png", width=120)
    st.markdown("## ⚙️ Settings")
    lang_display = st.selectbox(
        "🌐 Language / भाषा / भाषा",
        options=["Hindi", "Marathi", "English"],
        index=0,
    )
    LANG_MAP = {
        "Hindi":   {"code": "hi-IN", "short": "hi",  "label": "हिंदी"},
        "Marathi": {"code": "mr-IN", "short": "mr",  "label": "मराठी"},
        "English": {"code": "en-US", "short": "en",  "label": "English"},
    }
    lang = LANG_MAP[lang_display]

    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. 🎤 Click **Start** and speak your question")
    st.markdown("2. 🤖 AI Avenger reads & answers")
    st.markdown("3. 📖 Answer appears below in your language")

# ── Hero header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🎙️ Gram-Vani</h1>
  <p>सरकारी जानकारी अब आपकी भाषा में &nbsp;|&nbsp; Government info in your language</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Browser-native Speech-to-Text ─────────────────────────────────────────────
try:
    from streamlit_mic_recorder import speech_to_text
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

# Session state
if "last_question" not in st.session_state:
    st.session_state.last_question = ""
if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# ── Bedrock helper ─────────────────────────────────────────────────────────────
def get_bedrock_client():
    """Build a Bedrock runtime client from st.secrets (or env vars as fallback)."""
    try:
        key_id     = st.secrets.get("AWS_ACCESS_KEY_ID", "")
        secret_key = st.secrets.get("AWS_SECRET_ACCESS_KEY", "")
        region     = st.secrets.get("AWS_REGION", "us-east-1")
    except Exception:
        import os
        key_id     = os.getenv("AWS_ACCESS_KEY_ID", "")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        region     = os.getenv("AWS_REGION", "us-east-1")

    if not key_id or key_id.startswith("your-"):
        raise ValueError(
            "AWS credentials not set. Open `.streamlit/secrets.toml` and fill in "
            "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        )

    return boto3.client(
        "bedrock-runtime",
        region_name=region,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret_key,
    )


SYSTEM_PROMPTS = {
    "hi": (
        "आप एक सहायक हैं जो भारत सरकार की योजनाओं और दस्तावेज़ों के बारे में "
        "सरल हिंदी में जानकारी देते हैं। संक्षिप्त, स्पष्ट और उपयोगी उत्तर दें। "
        "उत्तर हमेशा हिंदी में ही दें।"
    ),
    "mr": (
        "तुम्ही एक सहाय्यक आहात जो भारत सरकारच्या योजना आणि दस्तऐवजांबद्दल "
        "सोप्या मराठीत माहिती देतो. संक्षिप्त, स्पष्ट आणि उपयुक्त उत्तर द्या. "
        "उत्तर नेहमी मराठीत द्या."
    ),
    "en": (
        "You are a helpful assistant that explains Indian government schemes and "
        "documents in simple English. Give concise, clear, and useful answers."
    ),
}


def ask_bedrock(question: str, lang_short: str) -> str:
    """Send question to Claude 3.5 Sonnet and return the answer text."""
    client = get_bedrock_client()
    system_prompt = SYSTEM_PROMPTS.get(lang_short, SYSTEM_PROMPTS["en"])

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "temperature": 0.3,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": question}
        ],
    }

    response = client.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body),
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


# ── Main interaction area ──────────────────────────────────────────────────────
st.subheader(f"🎤 Ask in {lang['label']}")
st.caption(f"Browser will use your microphone — make sure to allow access. Speaking in **{lang_display}**.")

col_voice, col_text = st.columns([1, 1], gap="medium")

with col_voice:
    st.markdown("**Option 1 — Speak your question:**")
    if MIC_AVAILABLE:
        spoken_text = speech_to_text(
            language=lang["code"],
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Stop & Transcribe",
            just_once=True,
            use_container_width=True,
            key=f"stt_{lang_display}",
        )
    else:
        st.warning(
            "⚠️ `streamlit-mic-recorder` not installed.\n\n"
            "Run: `pip install streamlit-mic-recorder` then restart."
        )
        spoken_text = None

with col_text:
    st.markdown("**Option 2 — Type your question:**")
    typed_text = st.text_area(
        "Type here…",
        placeholder="e.g. What is PM Kisan Samman Nidhi?",
        height=120,
        label_visibility="collapsed",
    )
    submit_typed = st.button("🔍 Get Answer", use_container_width=True, type="primary")

# Determine the active question
question = ""
if spoken_text and spoken_text.strip():
    question = spoken_text.strip()
elif submit_typed and typed_text.strip():
    question = typed_text.strip()

# ── Process & respond ──────────────────────────────────────────────────────────
if question and question != st.session_state.last_question:
    st.session_state.last_question = question
    st.session_state.last_answer = ""  # clear stale answer

    st.markdown(
        f'<div class="question-box">🗣️ <strong>You asked:</strong> {question}</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("🤖 AI Avenger is thinking…"):
        try:
            answer = ask_bedrock(question, lang["short"])
            st.session_state.last_answer = answer

        except ValueError as e:
            st.error(f"🔑 Credentials Error: {e}")
            st.info("Open `.streamlit/secrets.toml` and fill in your AWS keys, then restart the app.")
            st.stop()

        except (ClientError, NoCredentialsError) as e:
            st.error(f"☁️ AWS Error: {e}")
            st.stop()

        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            st.stop()

elif question and question == st.session_state.last_question:
    # Re-render: show the question again
    st.markdown(
        f'<div class="question-box">🗣️ <strong>You asked:</strong> {question}</div>',
        unsafe_allow_html=True,
    )

# Always show the last answer (persists across reruns)
if st.session_state.last_answer:
    st.markdown(
        f'<div class="answer-box">🤖 <strong>AI Avenger:</strong><br><br>{st.session_state.last_answer}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("")
    if st.button("🔄 Ask another question", use_container_width=True):
        st.session_state.last_question = ""
        st.session_state.last_answer = ""
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#aaa;font-size:0.85rem'>"
    "🇮🇳 Gram-Vani &nbsp;|&nbsp; AI Avenger Hackathon &nbsp;|&nbsp; "
    "Powered by AWS Bedrock Claude 3.5 Sonnet"
    "</div>",
    unsafe_allow_html=True,
)
