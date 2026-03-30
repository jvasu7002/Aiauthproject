import streamlit as st
import requests
import os
import google.generativeai as genai

# =========================
# 🔐 CONFIG
# =========================
st.set_page_config(page_title="Data Analyst AI", page_icon="📊")

st.title("📊 Data Analyst AI Assistant")

# =========================
# 🔑 API KEYS (SAFE LOAD)
# =========================

GEMINI_AVAILABLE = False
OPENROUTER_API_KEY = ""

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        GEMINI_AVAILABLE = True
except:
    pass

try:
    if "OPENROUTER_API_KEY" in st.secrets:
        OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
except:
    pass


# =========================
# 🌐 BACKEND URL
# =========================

BASE_URL = "https://aiauthproject.onrender.com/AIAuthProject"
REGISTER_URL = f"{BASE_URL}/register"
LOGIN_URL = f"{BASE_URL}/login"


# =========================
# 🧠 SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are an expert Data Analyst assistant.
Help with:
- SQL queries
- Python (Pandas, NumPy, Matplotlib)
- Data cleaning
- EDA
- Excel formulas
- Interview preparation

Always give practical examples with code.
"""


# =========================
# 🤖 AI FUNCTIONS
# =========================

def ask_gemini(user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(SYSTEM_PROMPT + "\nUser: " + user_input)
        return response.text
    except Exception as e:
        return None


def ask_openrouter(user_input):
    if not OPENROUTER_API_KEY:
        return None

    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "meta-llama/llama-3-8b-instruct",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        }

        res = requests.post(url, headers=headers, json=data)
        result = res.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

    except:
        pass

    return None


def offline_ai(user_input):
    user_input = user_input.lower()

    if "sql" in user_input:
        return "Example SQL:\nSELECT * FROM table WHERE condition;"

    elif "python" in user_input:
        return "Example:\nimport pandas as pd\ndf = pd.read_csv('data.csv')"

    elif "eda" in user_input:
        return "EDA = Exploratory Data Analysis using stats & visualization."

    return "⚠️ Offline mode response."


# =========================
# 🔐 AUTH FUNCTIONS
# =========================

def safe_json(response):
    try:
        return response.json()
    except:
        return {"status": "error", "message": response.text}


def login_user(username, password):
    try:
        res = requests.post(LOGIN_URL, data={
            "username": username,
            "password": password
        })
        return safe_json(res)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def register_user(username, password):
    try:
        res = requests.post(REGISTER_URL, data={
            "username": username,
            "password": password
        })
        return safe_json(res)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# =========================
# 🧠 SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# =========================
# 🔐 LOGIN PAGE
# =========================

if not st.session_state.logged_in:

    st.subheader("🔐 Login / Register")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            result = login_user(username, password)

            if result.get("status") == "success":
                st.session_state.logged_in = True
                st.success("Login Successful 🎉")
                st.rerun()
            else:
                st.error(result.get("message", "Invalid credentials ❌"))

    with tab2:
        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")

        if st.button("Register"):
            result = register_user(username, password)

            if result.get("status") == "success":
                st.success("Registered Successfully 🎉")
            else:
                st.error(result.get("message", "Registration Failed ❌"))


# =========================
# 🤖 CHAT PAGE
# =========================

else:

    st.success("Logged in successfully ✅")

    user_input = st.text_input("Ask your question")

    if st.button("Ask") and user_input:

        bot_reply = None

        # 1️⃣ Gemini
        if GEMINI_AVAILABLE:
            bot_reply = ask_gemini(user_input)

        # 2️⃣ OpenRouter fallback
        if not bot_reply:
            bot_reply = ask_openrouter(user_input)

        # 3️⃣ Offline fallback
        if not bot_reply:
            bot_reply = offline_ai(user_input)

        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", bot_reply))

    # Show chat
    for role, msg in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"**🧑 {role}:** {msg}")
        else:
            st.markdown(f"**🤖 {role}:** {msg}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.chat_history = []
        st.rerun()
