import json
import os
import bcrypt
import streamlit as st

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def signup(username: str, password: str, name: str) -> tuple[bool, str]:
    users = load_users()
    if username in users:
        return False, "Username already exists!"
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    users[username] = {
        "name": name,
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Account created successfully!"

def login(username: str, password: str) -> tuple[bool, str]:
    users = load_users()
    if username not in users:
        return False, "User not found."
    if not verify_password(password, users[username]["password"]):
        return False, "Incorrect password."
    return True, users[username]["name"]

def show_auth_page():
    st.markdown("""
    <div style='text-align:center; padding: 2rem 0 1rem 0;'>
        <div style='font-size:3.5rem;'>🤖</div>
        <h1 style='background: linear-gradient(135deg, #6C63FF, #3ECFCF);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                   font-size: 2.2rem; font-weight: 800; margin: 0;'>
            AI Business Analytics
        </h1>
        <p style='color: #888; margin-top: 0.3rem; font-size: 1rem;'>
            Your intelligent data analyst — powered by AI
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        with st.form("login_form"):
            st.subheader("Welcome back!")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login →", use_container_width=True)
            if submitted:
                ok, result = login(username, password)
                if ok:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["name"] = result
                    st.success(f"Welcome back, {result}! 🎉")
                    st.rerun()
                else:
                    st.error(result)
        st.info("💡 Demo: username `demo` / password `demo123`", icon="ℹ️")

    with tab2:
        with st.form("signup_form"):
            st.subheader("Create account")
            name = st.text_input("Full Name", placeholder="Your full name")
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
            submitted = st.form_submit_button("Create Account →", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match!")
                else:
                    ok, msg = signup(username, password, name)
                    if ok:
                        st.success(msg + " Please login.")
                    else:
                        st.error(msg)

def ensure_demo_user():
    users = load_users()
    if "demo" not in users:
        users["demo"] = {
            "name": "Demo User",
            "password": hash_password("demo123")
        }
        save_users(users)
