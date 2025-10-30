# app.py
import streamlit as st
from auth_pages import login_signup_page
from main_app import main_app_content
from mongo_handler import get_user_data

# --- Streamlit Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'signup_success' not in st.session_state:
    st.session_state['signup_success'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'upload'
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = False

# --- Logout function ---
def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.session_state['user_id'] = None
    st.session_state['current_page'] = "upload"
    st.session_state['data_loaded'] = False

    st.session_state['resume_uploaded'] = False
    st.session_state['analysis_result'] = None
    st.session_state['resume_text'] = None
    st.session_state['interests'] = None
    st.session_state['career_goal'] = None
    st.session_state['want_projects'] = False

    st.info("Logged out successfully.")

# --- Main Application Logic ---
if st.session_state['logged_in']:
    user_id = st.session_state['user_id']  # Pass user_id to main_app_content
    if not user_id:
        st.error("User ID not found! Please login again.")
    else:
        main_app_content(logout_user, user_id)
else:
    # Login/Signup page
    login_signup_page()
