import streamlit as st
import requests
import openai
import re

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Docdril AI Assistant", layout="centered")
st.title("🤖 Docdril AI Assistant")
st.caption("AI + Real-time Weather Intelligence")

# ---------------- SECRETS ----------------
if "OPENAI_API_KEY" not in st.secrets or "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("Missing API keys. Please add them in Streamlit Secrets.")
    st.stop()

openai.api_key = st.secrets["OPENAI_API_KEY"]
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me anything — I can also tell real-time weather 🌦️"}
    ]

# ---------------- HELPERS ----------------
def extract_city(text):
    match = re.search(r"in ([a-zA-Z ]+)", text.lower())
    return match.group(1).title() if match else None

def get_weather(city):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={WEATHER_KEY}&units=metric"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return None

    data = r.json()
    return {
        "city": city,
        "temp": data["main"]["temp"],
        "condition": data["weather"][0]["description"].title(),
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"]
    }

def openai_reply(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message["content"]

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response_text = ""

    # WEATHER INTENT CHECK
    if "weather" in user_input.lower() or "temperature" in user_input.lower():
        city = extract_city(user_input)
        if city:
            weather = get_weather(city)
            if weather:
                response_text = (
                    f"🌍 **Weather in {weather['city']}**\n\n"
                    f"🌡️ Temperature: **{weather['temp']}°C**\n"
                    f"☁️ Condition: **{weather['condition']}**\n"
                    f"💧 Humidity: **{weather['humidity']}%**\n"
                    f"🌬️ Wind Speed: **{weather['wind']} m/s**"
                )
            else:
                response_text = "❌ I couldn’t find weather data for that place."
        else:
            response_text = "Please mention a city name (e.g., *weather in Mumbai*)."
    else:
        response_text = openai_reply(
            [{"role": "system", "content": "You are a helpful assistant."}]
            + st.session_state.messages
        )

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
