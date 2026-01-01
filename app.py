import streamlit as st
import requests
import os
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="RoleAI",
    page_icon="🤖",
    layout="centered"
)

# ---------------- API KEY ----------------
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    st.error("Cohere API key not found in secrets.")
    st.stop()

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ai_name" not in st.session_state:
    st.session_state.ai_name = "RoleAI"

if "ai_role" not in st.session_state:
    st.session_state.ai_role = "A calm, intelligent AI that speaks clearly and confidently."

# ---------------- DRAMATIC BACKGROUND ----------------
st.markdown("""
<style>
body {
    margin: 0;
    background: #020617;
    color: white;
}

.aurora {
    position: fixed;
    inset: -50%;
    background:
        radial-gradient(circle at 20% 30%, rgba(99,102,241,0.4), transparent 40%),
        radial-gradient(circle at 80% 40%, rgba(34,211,238,0.35), transparent 45%),
        radial-gradient(circle at 50% 80%, rgba(168,85,247,0.3), transparent 40%);
    filter: blur(120px);
    animation: auroraMove 28s ease-in-out infinite;
    z-index: -2;
}

@keyframes auroraMove {
    0% { transform: translate(0,0) rotate(0deg); }
    50% { transform: translate(-8%, -6%) rotate(180deg); }
    100% { transform: translate(0,0) rotate(360deg); }
}

.core {
    width: 110px;
    height: 110px;
    margin: 12px auto 18px auto;
    border-radius: 50%;
    background: radial-gradient(circle, #a5b4fc, #6366f1 45%, #020617 70%);
    box-shadow: 0 0 50px rgba(99,102,241,0.7);
    animation: pulse 3.8s ease-in-out infinite;
}

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.08); }
    100% { transform: scale(1); }
}

.chat {
    max-width: 82%;
    padding: 14px 18px;
    margin: 10px 0;
    border-radius: 18px;
    line-height: 1.5;
    backdrop-filter: blur(10px);
}

.user {
    background: linear-gradient(135deg, #4f46e5, #6366f1);
    margin-left: auto;
    text-align: right;
}

.ai {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
}

input {
    background: rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
    color: white !important;
}

.thinking {
    font-style: italic;
    opacity: 0.7;
    animation: breathe 2s ease-in-out infinite;
}

@keyframes breathe {
    0% { opacity: 0.4; }
    50% { opacity: 1; }
    100% { opacity: 0.4; }
}
</style>

<div class="aurora"></div>
""", unsafe_allow_html=True)

# ---------------- SETTINGS ----------------
with st.expander("⚙️ AI Settings"):
    st.session_state.ai_name = st.text_input("AI Name", st.session_state.ai_name)
    st.session_state.ai_role = st.text_area(
        "AI Role / Personality",
        st.session_state.ai_role,
        height=120
    )

# ---------------- HEADER ----------------
st.markdown(f"""
<h2 style="text-align:center;">🤖 {st.session_state.ai_name}</h2>
<p style="text-align:center;opacity:0.75;">
{st.session_state.ai_role}
</p>
""", unsafe_allow_html=True)

st.markdown("<div class='core'></div>", unsafe_allow_html=True)

# ---------------- CHAT HISTORY ----------------
for msg in st.session_state.messages:
    cls = "user" if msg["role"] == "user" else "ai"
    st.markdown(
        f"<div class='chat {cls}'>{msg['content']}</div>",
        unsafe_allow_html=True
    )

# ---------------- INPUT ----------------
with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("", placeholder="Speak to the AI…")
    send = st.form_submit_button("Send")

# ---------------- COHERE CHAT (CURRENT MODEL) ----------------
if send and user_text.strip():
    st.session_state.messages.append({
        "role": "user",
        "content": user_text
    })

    thinking_box = st.empty()
    thinking_box.markdown(
        "<div class='chat ai thinking'>Processing…</div>",
        unsafe_allow_html=True
    )

    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "command",
        "message": user_text,
        "preamble": f"You are {st.session_state.ai_name}. {st.session_state.ai_role}",
        "temperature": 0.6
    }

    try:
        response = requests.post(
            "https://api.cohere.ai/v1/chat",
            headers=headers,
            json=payload,
            timeout=30
        )
        data = response.json()
        ai_reply = data.get("text", "⚠️ No response.")

    except Exception:
        ai_reply = "⚠️ Connection error."

    thinking_box.empty()

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_reply
    })

    st.rerun()
