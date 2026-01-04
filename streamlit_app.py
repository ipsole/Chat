
import streamlit as st
import openai

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Docdril AI Chat", layout="centered")

# ---------------- API KEY ----------------
if "OPENAI_API_KEY" not in st.secrets:
    st.error("OpenAI API key not found. Please add it to Streamlit secrets.")
    st.stop()

openai.api_key = st.secrets["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"]

MODEL = "gpt-4o-mini"

# ---------------- STYLES ----------------
st.markdown(
    '''
    <style>
    .chat-container { max-width: 720px; margin: auto; }
    .user-msg {
        background:#10b981; color:white; padding:12px 16px;
        border-radius:18px 18px 4px 18px; margin:8px 0;
    }
    .ai-msg {
        background:#ffffff; border:1px solid #e5e7eb; color:#111827;
        padding:12px 16px; border-radius:18px 18px 18px 4px; margin:8px 0;
    }
    .meta { font-size:11px; color:#9ca3af; margin-bottom:6px; }
    </style>
    ''',
    unsafe_allow_html=True
)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI assistant. How can I help you today?"}
    ]

# ---------------- HEADER ----------------
st.markdown("## 🤖 Docdril AI Chat")
st.caption("Powered by OpenAI")

col1, col2 = st.columns([1, 1])
with col2:
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Chat cleared. How else can I help?"}
        ]
        st.experimental_rerun()

# ---------------- CHAT MESSAGES ----------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-msg">{msg["content"]}</div><div class="meta">You</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg">{msg["content"]}</div><div class="meta">AI</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- INPUT ----------------
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask anything…", "")
    send = st.form_submit_button("Send")

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Thinking…"):
        try:
            response = openai.ChatCompletion.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful and professional AI assistant."},
                    *st.session_state.messages
                ],
                temperature=0.7
            )
            ai_reply = response.choices[0].message["content"]
        except Exception as e:
            ai_reply = f"⚠️ Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.experimental_rerun()
