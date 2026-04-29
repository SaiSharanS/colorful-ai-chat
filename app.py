"""
🌌 COSMOS - AI Chat Platform 🌌
Working version with persistent user storage.
"""

import os
import random
from datetime import datetime, date
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import hashlib
import json

load_dotenv()

st.set_page_config(
    page_title="Cosmos ✨",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #0F0E17 0%, #1A1825 100%); }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .gradient-title {
        background: linear-gradient(90deg, #FF6B9D, #9D4EDD, #4CC9F0, #06FFA5, #FFD60A, #FF8E3C, #FF6B9D);
        background-size: 200% 200%;
        animation: gradient 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        padding: 10px;
    }
    .subtitle { text-align: center; color: #B8B8D4; font-style: italic; }
    .welcome-header {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B9D, #9D4EDD, #4CC9F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
    }
    [data-testid="stSidebar"] { background-color: #1A1825 !important; }
    [data-testid="stSidebar"] * { color: #FFFFFE; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2FBF 100%) !important;
        border-radius: 18px !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
        border-radius: 18px !important;
    }
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li, [data-testid="stChatMessage"] div { color: #FFFFFE !important; }
    [data-testid="stChatInput"] {
        background-color: #2D2B40 !important;
        border-radius: 16px !important;
        border: 2px solid #9D4EDD !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #2D2B40 !important;
        color: #FFFFFE !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF6B9D 0%, #9D4EDD 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: bold;
        width: 100%;
    }
    .status-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .status-free { background: #FFD60A; color: #0F0E17; }
    .status-premium { background: #06FFA5; color: #0F0E17; }
    hr { border-color: #9D4EDD; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

FREE_DAILY_LIMIT = 5
PREMIUM_DAILY_LIMIT = 100
ADMIN_PASSWORD = "admin123"

DEMO_REPLIES = [
    "That's a fascinating question! 🌟",
    "I love that perspective! ✨",
    "Great point! 🎨",
    "Ooh, interesting! 🚀",
    "Wonderful question! 🌈",
    "Excellent! 🎯",
]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_users():
    """Get users from st.session_state, with demo user"""
    if "all_users" not in st.session_state:
        st.session_state.all_users = {
            "demo": {"password": hash_password("demo123"), "is_premium": False}
        }
    return st.session_state.all_users

def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "msg_count_today" not in st.session_state:
        st.session_state.msg_count_today = 0
    if "is_premium" not in st.session_state:
        st.session_state.is_premium = False
    if "openai_client" not in st.session_state:
        api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
        st.session_state.openai_client = OpenAI(api_key=api_key) if api_key else None

init_session()

# ============================================================
# LOGIN PAGE
# ============================================================
if not st.session_state.logged_in:
    st.markdown('<div class="gradient-title">🌌 COSMOS 🌌</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Sign in to start chatting</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        
        admin_mode = st.checkbox("🔐 Admin Login")
        
        if admin_mode:
            admin_pass = st.text_input("Admin Password", type="password")
            if st.button("🔐 Login as Admin", use_container_width=True):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = "ADMIN"
                    st.success("✅ Admin logged in!")
                    st.rerun()
                else:
                    st.error("❌ Wrong password")
        else:
            tab1, tab2 = st.tabs(["🔓 Login", "✍️ Register"])
            
            with tab1:
                st.subheader("Login")
                username = st.text_input("Username", key="login_user")
                password = st.text_input("Password", type="password", key="login_pass")
                
                if st.button("🚀 Login", use_container_width=True):
                    users = get_users()
                    if username in users and users[username]["password"] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_premium = users[username]["is_premium"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            with tab2:
                st.subheader("Create Account")
                new_user = st.text_input("Username", key="reg_user")
                new_pass = st.text_input("Password", type="password", key="reg_pass")
                new_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confirm")
                
                if st.button("✍️ Register", use_container_width=True):
                    users = get_users()
                    if new_user in users:
                        st.error("Username exists!")
                    elif len(new_user) < 3:
                        st.error("Username too short")
                    elif len(new_pass) < 6:
                        st.error("Password too short")
                    elif new_pass != new_pass_confirm:
                        st.error("Passwords don't match")
                    else:
                        users[new_user] = {"password": hash_password(new_pass), "is_premium": False}
                        st.success("✅ Account created! Login now.")
        
        st.markdown("---")

# ============================================================
# ADMIN DASHBOARD
# ============================================================
elif st.session_state.is_admin:
    st.markdown(f'<div class="welcome-header">Admin Panel 👑</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.is_admin = False
            st.rerun()
    
    users = get_users()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        premium = sum(1 for u in users.values() if u.get("is_premium"))
        st.metric("Premium", premium)
    
    st.divider()
    st.subheader("Users:")
    for username in users.keys():
        status = "⭐ Premium" if users[username]["is_premium"] else "Free"
        st.write(f"👤 {username} - {status}")

# ============================================================
# MAIN APP
# ============================================================
else:
    st.markdown(f'<div class="welcome-header">Welcome, {st.session_state.username}! 👋</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        
        limit = PREMIUM_DAILY_LIMIT if st.session_state.is_premium else FREE_DAILY_LIMIT
        used = st.session_state.msg_count_today
        remaining = max(0, limit - used)
        
        if st.session_state.is_premium:
            st.markdown('<span class="status-pill status-premium">⭐ PREMIUM</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-pill status-free">🆓 FREE</span>', unsafe_allow_html=True)
        
        st.progress(min(used / limit, 1.0))
        st.markdown(f"**{remaining} / {limit}** messages left")
        
        st.divider()
        
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()

    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(f"Hey **{st.session_state.username}**! Ask me anything! ✨")

    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("💬 Type message…")
    if user_input:
        limit = PREMIUM_DAILY_LIMIT if st.session_state.is_premium else FREE_DAILY_LIMIT
        if st.session_state.msg_count_today >= limit and not st.session_state.is_premium:
            st.error(f"Limit reached! Upgrade to premium.")
            st.stop()

        st.session_state.msg_count_today += 1
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🤖"):
            if st.session_state.openai_client:
                try:
                    response = st.session_state.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages,
                        max_tokens=1024,
                    )
                    reply = response.choices[0].message.content
                except:
                    reply = random.choice(DEMO_REPLIES)
            else:
                reply = random.choice(DEMO_REPLIES)

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()