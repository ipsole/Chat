import streamlit as st
import requests
import openai

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Docdril Weather AI", layout="centered")
st.title("🌦️ Docdril Weather AI")
st.caption("Ask in natural language. Get real-time weather.")

# ---------------- SECRETS ----------------
if "OPENAI_API_KEY" not in st.secrets or "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("Missing API keys. Add them in Streamlit Secrets.")
    st.stop()

openai.api_key = st.secrets["OPENAI_API_KEY"]
WEATHER_KEY = st.secrets["OPENWEATHER_API_KEY"]

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi 👋 Ask me about the weather of any city (e.g. *What’s the weather in Mumbai?*)"
        }
    ]

# ---------------- FUNCTIONS ----------------
def extract_city_with_ai(user_text):
    """
    Use OpenAI ONLY to extract city name.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract ONLY the city name from the user message. If no city is mentioned, respond with NONE."
            },
            {"role": "user", "content": user_text}
        ],
        temperature=0
    )

    city = response.choices[0].message["content"].strip()
    return None if city.upper() == "NONE" else city


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
        "city": data["name"],
        "temp": data["main"]["temp"],
        "feels": data["main"]["feels_like"],
        "condition": data["weather"][0]["description"].title(),
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"]
    }


def format_weather(w):
    return (
        f"🌍 **Weather in {w['city']}**\n\n"
        f"🌡️ Temperature: **{w['temp']}°C**\n"
        f"🤒 Feels Like: **{w['feels']}°C**\n"
        f"☁️ Condition: **{w['condition']}**\n"
        f"💧 Humidity: **{w['humidity']}%**\n"
        f"🌬️ Wind Speed: **{w['wind']} m/s**"
    )

# ---------------- CHAT DISPLAY ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask about weather of any city…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Fetching real-time weather..."):
        city = extract_city_with_ai(user_input)

        if not city:
            reply = "❌ Please mention a city name (e.g. *weather in Delhi*)."
        else:
            weather = get_weather(city)
            if not weather:
                reply = f"❌ I couldn’t find weather data for **{city}**."
            else:
                reply = format_weather(weather)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
