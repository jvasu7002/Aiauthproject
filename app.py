import streamlit as st
import requests
import google.generativeai as genai
import os
import pandas as pd
import matplotlib.pyplot as plt

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    pass
# ===== Gemini Setup =====
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-pro")

response = model.generate_content("Hello")
print(response.text)

# ===== OpenRouter Key =====
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

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

Always give practical examples with code.
"""

# ===== API URLs =====
REGISTER_URL = "https://aiauthproject.onrender.com/AIAuthProject/register"
LOGIN_URL = "https://aiauthproject.onrender.com/AIAuthProject/login"

st.set_page_config(page_title="Data Analyst AI", page_icon="📊")

# ===== SESSION =====
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ===== AUTH =====
def login_user(username, password):
    try:
        res = requests.post(LOGIN_URL, data={
            "username": username,
            "password": password
        })

        print("LOGIN STATUS:", res.status_code)
        print("LOGIN RAW:", res.text)

        if res.text.strip() == "":
            return {"status": "error", "message": "Empty response from server"}

        try:
            return res.json()
        except:
            return {"status": "error", "message": res.text}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def register_user(username, password):
    try:
        res = requests.post(REGISTER_URL, data={
            "username": username,
            "password": password
        })

        print("REGISTER STATUS:", res.status_code)
        print("REGISTER RAW:", res.text)

        if res.text.strip() == "":
            return {"status": "error", "message": "Empty response from server"}

        try:
            return res.json()
        except:
            return {"status": "error", "message": res.text}

    except Exception as e:
        return {"status": "error", "message": str(e)}
# ===== OPENROUTER =====
def ask_openrouter(user_input):
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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        result = res.json()
        return result["choices"][0]["message"]["content"] if "choices" in result else "⚠️ OpenRouter Error"
    except:
        return "⚠️ OpenRouter Failed"

# ===== OFFLINE =====
def offline_ai(user_input):
    if "sql" in user_input.lower():
        return "SELECT * FROM table WHERE condition;"
    elif "excel" in user_input.lower():
        return "=SUM(A1:A10), =AVERAGE(A1:A10), =IF(A1>50,\"Pass\",\"Fail\")"
    return "⚠️ Offline response only."

# ===== LOGIN PAGE =====
if not st.session_state.logged_in:

    st.title("🔐 Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    # ===== LOGIN =====
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            result = login_user(u, p)

            if result.get("status") == "success":
                st.session_state.logged_in = True
                st.success("Login Successful 🎉")
                st.rerun()
            else:
                st.error(result.get("message", "Invalid login"))

    # ===== REGISTER =====
    with tab2:
        u2 = st.text_input("New Username")
        p2 = st.text_input("New Password", type="password")

        if st.button("Register"):
            result = register_user(u2, p2)

            if result.get("status") == "success":
                st.success("Registered Successfully 🎉")
            else:
                st.error(result.get("message", "Registration Failed"))

# ===== MAIN APP =====
else:

    st.title("📊 Data Analyst AI Assistant")
    st.success("Logged in successfully ✅")

    # ===== CSV =====
    st.subheader("📂 Upload CSV")
    file = st.file_uploader("Upload", type=["csv"])

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
            try:
                res = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=summary
                )
                st.write(res.text)
            except:
                st.write(ask_openrouter(summary))

    # ===== CHAT =====
    user_input = st.text_input("Ask question")

    if st.button("Ask") and user_input:

        context = ""
        for r, m in st.session_state.chat_history[-4:]:
            context += f"{r}:{m}\n"

        try:
            res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=context + user_input
            )
            reply = res.text
        except:
            try:
                reply = ask_openrouter(user_input)
            except:
                reply = offline_ai(user_input)

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
