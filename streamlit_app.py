
import streamlit as st
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Docdril AI Chat", layout="centered")

client = OpenAI(api_key=st.secrets.get("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", None))
MODEL = "gpt-4o-mini"

# ---------------- STYLES ----------------
st.markdown(
    '''
    <style>
    .chat-container { max-width: 700px; margin: auto; }
    .user-msg {
        background:#10b981; color:white; padding:12px 16px;
        border-radius:18px 18px 4px 18px; margin:8px 0;
    }
    .ai-msg {
        background:#ffffff; border:1px solid #e5e7eb; color:#111827;
        padding:12px 16px; border-radius:18px 18px 18px 4px; margin:8px 0;
    }
    .meta { font-size:11px; color:#9ca3af; margin-top:2px; }
    </style>
    ''',
    unsafe_allow_html=True
)

# ---------------- STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI assistant. How can I help you today?"}
    ]

# ---------------- HEADER ----------------
st.markdown("## 🤖 Docdril AI Chat")
st.caption("Powered by GPT‑4o mini")

if st.button("🗑 Clear Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Chat cleared. How else can I help?"}
    ]
    st.experimental_rerun()

# ---------------- CHAT ----------------
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
    submitted = st.form_submit_button("Send")

if submitted and user_input.strip():
    if not client.api_key:
        st.error("OpenAI API key missing. Add it to Streamlit secrets.")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking…"):
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful and professional AI assistant."},
                    *st.session_state.messages
                ],
                temperature=0.7
            )

            ai_text = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_text})

        st.experimental_rerun()
