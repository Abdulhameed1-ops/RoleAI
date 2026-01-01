import streamlit as st
import requests
import time
import uuid

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="RoleAI",
    page_icon="🤖",
    layout="centered"
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "ai_name" not in st.session_state:
    st.session_state.ai_name = "RoleAI"

if "ai_role" not in st.session_state:
    st.session_state.ai_role = "A helpful and friendly AI assistant"

# ---------------- CSS (UI + ANIMATIONS) ----------------
st.markdown("""
<style>
body {
    background: radial-gradient(circle at top, #0f172a, #020617);
    color: white;
}

/* floating background animation */
.bg {
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
}

.bg span {
    position: absolute;
    display: block;
    width: 20px;
    height: 20px;
    background: rgba(99,102,241,0.15);
    animation: float 20s linear infinite;
    border-radius: 50%;
}

@keyframes float {
    0% { transform: translateY(100vh) scale(0); }
    100% { transform: translateY(-10vh) scale(1); }
}

/* chat bubbles */
.chat {
    max-width: 85%;
    padding: 14px 18px;
    margin: 10px 0;
    border-radius: 18px;
    line-height: 1.5;
}

.user {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    margin-left: auto;
    text-align: right;
}

.ai {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
}

/* input box */
.input-box {
    background: rgba(255,255,255,0.08);
    padding: 12px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* send button */
.send-btn {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border: none;
    padding: 12px 18px;
    border-radius: 14px;
    color: white;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.send-btn:hover {
    transform: scale(1.05);
}

/* thinking dots */
.thinking span {
    animation: blink 1.4s infinite both;
}
.thinking span:nth-child(2) { animation-delay: 0.2s; }
.thinking span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink {
    0% { opacity: .2; }
    20% { opacity: 1; }
    100% { opacity: .2; }
}
</style>
""", unsafe_allow_html=True)

# floating particles
st.markdown("""
<div class="bg">
""" + "".join([f"<span style='left:{i*7}%;animation-delay:{i}s'></span>" for i in range(15)]) + """
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR SETTINGS ----------------
st.sidebar.title("⚙️ RoleAI Settings")

st.session_state.ai_name = st.sidebar.text_input(
    "AI Name",
    st.session_state.ai_name
)

st.session_state.ai_role = st.sidebar.text_area(
    "AI Role / Personality",
    st.session_state.ai_role,
    height=120
)

cohere_api_key = st.sidebar.text_input(
    "Cohere API Key",
    type="password"
)

st.sidebar.markdown("---")
st.sidebar.markdown("🧠 **RoleAI** – Chat with AI characters")

# ---------------- HEADER ----------------
st.markdown(f"""
<h1 style="text-align:center;">🤖 {st.session_state.ai_name}</h1>
<p style="text-align:center;opacity:0.8;">
{st.session_state.ai_role}
</p>
""", unsafe_allow_html=True)

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "ai"
    st.markdown(
        f"<div class='chat {role_class}'>{msg['content']}</div>",
        unsafe_allow_html=True
    )

# ---------------- INPUT ----------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "",
        placeholder="Type your message...",
        key=str(uuid.uuid4())
    )

    send = st.form_submit_button("Send")

# ---------------- AI RESPONSE ----------------
if send and user_input.strip():
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    thinking_placeholder = st.empty()
    thinking_placeholder.markdown(
        f"<div class='chat ai thinking'>Thinking<span>.</span><span>.</span><span>.</span></div>",
        unsafe_allow_html=True
    )

    time.sleep(0.8)

    headers = {
        "Authorization": f"Bearer {cohere_api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are {st.session_state.ai_name}.
Your role: {st.session_state.ai_role}.

Conversation:
"""

    for m in st.session_state.messages:
        prompt += f"{m['role'].upper()}: {m['content']}\n"

    prompt += "AI:"

    try:
        response = requests.post(
            "https://api.cohere.ai/v1/chat",
            headers=headers,
            json={
                "model": "command",
                "prompt": prompt,
                "max_tokens": 300,
                "temperature": 0.7
            }
        )

        result = response.json()
        ai_text = result["generations"][0]["text"].strip()

    except Exception as e:
        ai_text = "⚠️ Error connecting to AI."

    thinking_placeholder.empty()

    st.session_state.messages.append({
        "role": "ai",
        "content": ai_text
    })

    st.rerun()