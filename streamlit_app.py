import os
import streamlit as st
import requests
from openai import OpenAI
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
    """Fetch current weather data from OpenWeatherMap."""
    if not api_key:
        return "⚠️ Weather API key is missing."
    
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            return (f"The current weather in **{city.title()}** is {desc} with a temperature of **{temp}°C**. "
                    f"Humidity is at {humidity}% and wind speed is {wind} m/s.")
        else:
            return f"⚠️ Could not find weather for '{city}'. (Error: {data.get('message', 'Unknown')})"
    except Exception as e:
        return f"⚠️ Error fetching weather: {str(e)}"

# --- Sidebar: API Keys & Settings ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("Enter your API keys below to enable features.")
    
    openai_key = st.text_input("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", type="password", placeholder="sk-...")
    weather_key = st.text_input("90c79b684ef8183616c24326a8ce5c59", type="password", placeholder="Paste key here...")
    
    st.divider()
    model_choice = st.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o"], index=0)
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Main UI ---
st.title("🌤️ AI & Weather Assistant")
st.caption("Ask me about the weather or chat about anything else!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Logic ---
if prompt := st.chat_input("What's the weather like in London?"):
    # Check for API keys
    if not openai_key:
        st.error("Please provide an OpenAI API Key in the sidebar.")
        st.stop()

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 1. Natural Language Intent Detection (Simple approach)
    # We ask the AI if the user is asking for weather, or just process normally.
    client = OpenAI(api_key=openai_key)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Intent analysis: Check if user is asking for weather
                intent_prompt = f"Does the following text ask for a weather report for a specific city? If yes, respond ONLY with the city name. If no, respond with 'NO'. Text: '{prompt}'"
                
                intent_check = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "You are an intent classifier."},
                              {"role": "user", "content": intent_prompt}]
                )
                
                intent_res = intent_check.choices[0].message.content.strip().replace(".", "")
                
                # 2. Handle Weather or General Chat
                if intent_res.upper() != "NO" and len(intent_res) < 50:
                    # Weather Path
                    weather_report = get_weather(intent_res, weather_key)
                    
                    # Optional: Pass weather data back to GPT to make it sound natural
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Use the provided weather data to answer the user's request naturally."},
                            {"role": "user", "content": f"User asked: {prompt}. Weather data: {weather_report}"}
                        ]
                    )
                    full_response = response.choices[0].message.content
                else:
                    # Standard Chat Path
                    response = client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": "You are a helpful and professional AI assistant."},
                            *st.session_state.messages
                        ]
                    )
                    full_response = response.choices[0].message.content

                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: grey; font-size: 0.8rem;'>{datetime.now().year} AI Weather Bot | Built with Streamlit</p>", unsafe_allow_html=True)
