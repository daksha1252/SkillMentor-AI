import streamlit as st
import requests
import json
from firebase_config import firebaseConfig

API_KEY = firebaseConfig.get("apiKey")
AUTH_URL = "https://identitytoolkit.googleapis.com/v1"

def signup_user(email, password):
    try:
        url = f"{AUTH_URL}/accounts:signUp?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, data=json.dumps(payload))
        response.raise_for_status()
        st.session_state['signup_success'] = True
        st.success("Account created successfully! Please log in.")
        return True
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            st.error("Error creating account: This email is already registered.")
        elif "WEAK_PASSWORD" in error_message:
            st.error("Error creating account: Password should be at least 6 characters.")
        elif "INVALID_EMAIL" in error_message:
            st.error("Error creating account: Invalid email address.")
        else:
            st.error(f"Error creating account: {error_message}")
        return False

def login_user(email, password):
    try:
        url = f"{AUTH_URL}/accounts:signInWithPassword?key={API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, data=json.dumps(payload))
        response.raise_for_status()
        
        user_response = response.json()
        st.session_state['logged_in'] = True
        st.session_state['user_info'] = email
        st.session_state['user_id'] = user_response.get('localId') # Store the unique UID
        
        st.success(f"Logged in as {email}!")
        st.rerun()
        return True
    except requests.exceptions.RequestException as e:
        error_message = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_message:
            st.error("Error logging in: Invalid email or password.")
        elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
            st.error("Error logging in: Too many failed login attempts. Please try again later.")
        else:
            st.error(f"Error logging in: {error_message}")
        return False

def login_signup_page():
    st.set_page_config(page_title="Login/Signup - SkillMentor AI", layout="centered")
    st.title("SkillMentor AI - Login/Signup")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login to your account")
        login_email = st.text_input("Email (Login)", key="login_email")
        login_password = st.text_input("Password (Login)", type="password", key="login_password")
        if st.button("Login", key="login_button"):
            if login_email and login_password:
                login_user(login_email, login_password)
            else:
                st.warning("Please enter both email and password.")

    with tab2:
        st.subheader("Create a new account")
        signup_email = st.text_input("Email (Sign Up)", key="signup_email")
        signup_password = st.text_input("Password (Sign Up)", type="password", key="signup_password")
        signup_confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
        if st.button("Sign Up", key="signup_button"):
            if signup_email and signup_password and signup_confirm_password:
                if signup_password == signup_confirm_password:
                    if signup_user(signup_email, signup_password):
                        st.session_state['signup_email_val'] = ""
                        st.session_state['signup_password_val'] = ""
                        st.session_state['signup_confirm_password_val'] = ""
                else:
                    st.error("Passwords do not match!")
            else:
                st.warning("Please fill in all fields.")
