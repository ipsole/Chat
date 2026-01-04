import os
import streamlit as st
import requests
import openai
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="AI & Weather Assistant",
    page_icon="🌤️",
    layout="centered"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Helper Functions ---

def get_weather(city, api_key):
    if not api_key:
        return "⚠️ Weather API key is missing."
    
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={api_key}&units=metric"
    )

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if r.status_code == 200:
            return {
                "city": data["name"],
                "temp": data["main"]["temp"],
                "desc": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"]
            }
        else:
            return None
    except Exception:
        return None


def format_weather(w):
    return (
        f"🌍 **Weather in {w['city']}**\n\n"
        f"🌡️ Temperature: **{w['temp']}°C**\n"
        f"☁️ Condition: **{w['desc']}**\n"
        f"💧 Humidity: **{w['humidity']}%**\n"
        f"🌬️ Wind Speed: **{w['wind']} m/s**"
    )

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")

    openai_key = st.text_input("OpenAI API Key", type="password")
    weather_key = st.text_input("OpenWeatherMap Key", type="password")

    model_choice = st.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o"], index=0)

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- OpenAI Setup ---
if openai_key:
    openai.api_key = openai_key

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- UI ---
st.title("🌤️ AI & Weather Assistant")
st.caption("Ask me about the weather or anything else.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Chat Input ---
if prompt := st.chat_input("What's the weather like in London?"):
    if not openai_key:
        st.error("Please provide an OpenAI API Key.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # ---- Intent detection ----
                intent = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Extract ONLY the city name if the user asks about weather. Otherwise reply NO."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0
                )

                city = intent.choices[0].message["content"].strip()

                if city.upper() != "NO" and weather_key:
                    weather = get_weather(city, weather_key)
                    if weather:
                        full_response = format_weather(weather)
                    else:
                        full_response = f"❌ Could not fetch weather for **{city}**."
                else:
                    response = openai.ChatCompletion.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": "You are a helpful and professional assistant."},
                            *st.session_state.messages
                        ]
                    )
                    full_response = response.choices[0].message["content"]

                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"Error: {e}")

# --- Footer ---
st.markdown("---")
st.markdown(
    f"<p style='text-align:center; color:grey; font-size:0.8rem;'>"
    f"{datetime.now().year} AI Weather Bot | Built with Streamlit</p>",
    unsafe_allow_html=True
)
