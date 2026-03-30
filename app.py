import streamlit as st
import requests
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt

# ===== PAGE CONFIG =====
st.set_page_config(page_title="Data Analyst AI", page_icon="📊")

# ===== GEMINI SETUP =====
model = None
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
except Exception as e:
    st.sidebar.error(f"Gemini Error: {e}")

# ===== OPENROUTER KEY =====
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = """
You are an expert Data Analyst assistant.
Help with:
- SQL queries
- Python (Pandas, NumPy, Matplotlib)
- Data cleaning
- EDA
- Excel formulas
- Interview preparation
"""

# ===== API URLs =====
REGISTER_URL = "https://aiauthproject.onrender.com/AIAuthProject/register"
LOGIN_URL = "https://aiauthproject.onrender.com/AIAuthProject/login"

# ===== SESSION =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===== SAFE JSON =====
def safe_json(res):
    try:
        return res.json()
    except:
        return {
            "status": "error",
            "message": f"Server Error: {res.text[:100]}"
        }

# ===== AUTH =====
def login_user(username, password):
    try:
        res = requests.post(LOGIN_URL, data={"username": username, "password": password})

        if res.status_code != 200:
            return {"status": "error", "message": f"Server Down ({res.status_code})"}

        return safe_json(res)

    except Exception as e:
        return {"status": "error", "message": str(e)}

def register_user(username, password):
    try:
        res = requests.post(REGISTER_URL, data={"username": username, "password": password})

        if res.status_code != 200:
            return {"status": "error", "message": f"Server Down ({res.status_code})"}

        return safe_json(res)

    except Exception as e:
        return {"status": "error", "message": str(e)}

# ===== OPENROUTER =====
def ask_openrouter(user_input):
    if not OPENROUTER_API_KEY:
        return "⚠️ OpenRouter API key missing."

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "Data Analyst AI",
        "Content-Type": "application/json"
    }

    data = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        result = res.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"⚠️ OpenRouter Failed: {result}"

    except Exception as e:
        return f"⚠️ OpenRouter Error: {e}"

# ===== AI RESPONSE =====
def get_ai_response(prompt):
    if model:
        try:
            res = model.generate_content(prompt)
            return res.text
        except Exception as e:
            st.warning(f"Gemini failed: {e}")

    return ask_openrouter(prompt)

# ===== LOGIN PAGE =====
if not st.session_state.logged_in:

    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            result = login_user(u, p)
            if result.get("status") == "success":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error(result.get("message", "Login failed"))

    with tab2:
        u2 = st.text_input("New Username")
        p2 = st.text_input("New Password", type="password")

        if st.button("Register"):
            result = register_user(u2, p2)
            if result.get("status") == "success":
                st.success("Registered Successfully 🎉")
            else:
                st.error(result.get("message", "Registration failed"))

# ===== MAIN APP =====
else:

    st.title("📊 Data Analyst AI Assistant")

    # ===== CSV =====
    st.subheader("📂 Upload CSV")
    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        st.dataframe(df.head())
        st.write(df.describe())

        col = st.selectbox("Select column", df.columns)

        if st.button("Generate Graph"):
            plt.figure()
            df[col].hist()
            st.pyplot(plt)

        if st.button("Analyze Dataset"):
            summary = df.describe().to_string()
            st.write(get_ai_response(summary))

    # ===== CHAT =====
    user_input = st.text_input("Ask question")

    if st.button("Ask") and user_input:
        reply = get_ai_response(user_input)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", reply))

    # ===== CHAT UI =====
    for role, msg in st.session_state.chat_history:
        st.markdown(f"""
        <div style='background:#111;padding:10px;border-radius:10px;margin:5px'>
        <b>{role}:</b> {msg}
        </div>
        """, unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.chat_history = []
        st.rerun()
