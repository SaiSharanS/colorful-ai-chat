"""
🌌 COSMOS - AI Chat Platform 🌌
A beautiful, vibrant AI chatbot interface.

Features:
  - Beautiful neon dark theme
  - OpenAI GPT integration
  - GOOGLE SIGN-IN + Traditional Login
  - USER ANALYTICS (who signed in, what they searched, time spent)
  - Freemium model (5 free messages/day, unlimited for premium)
  - Admin Dashboard to view all user data
  - Ready to monetize

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

Deploy:
    Push to GitHub → Connect to streamlit.io/cloud → Live URL in 2 minutes
"""

import os
import random
from datetime import datetime, date, timedelta
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import hashlib
import pandas as pd
import json

load_dotenv()

# ============================================================
# 📱 PAGE CONFIG (must be first Streamlit command)
# ============================================================
st.set_page_config(
    page_title="Cosmos ✨",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 🎨 CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    /* Hide Streamlit branding for clean look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0F0E17 0%, #1A1825 100%);
    }

    /* Animated gradient title */
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

    .subtitle {
        text-align: center;
        color: #B8B8D4;
        font-style: italic;
        font-size: 0.95em;
        margin-bottom: 20px;
    }

    .welcome-header {
        font-size: 2.5em;
        font-weight: bold;
        background: linear-gradient(90deg, #FF6B9D, #9D4EDD, #4CC9F0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 20px 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A1825 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFE; }

    /* Chat messages */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2FBF 100%) !important;
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(157, 78, 221, 0.3);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] div { color: #FFFFFE !important; }

    /* Chat input */
    [data-testid="stChatInput"] {
        background-color: #2D2B40 !important;
        border-radius: 16px !important;
        border: 2px solid #9D4EDD !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #2D2B40 !important;
        color: #FFFFFE !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #FF6B9D 0%, #9D4EDD 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        font-weight: bold;
        padding: 10px 20px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #9D4EDD 0%, #4CC9F0 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(157, 78, 221, 0.4);
    }

    /* Premium upgrade banner */
    .premium-banner {
        background: linear-gradient(135deg, #FFD60A 0%, #FF8E3C 100%);
        color: #0F0E17;
        padding: 16px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin: 14px 0;
        box-shadow: 0 4px 12px rgba(255, 214, 10, 0.4);
    }

    /* Status pill */
    .status-pill {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        margin: 8px 0;
    }
    .status-free   { background: #FFD60A; color: #0F0E17; }
    .status-premium { background: #06FFA5; color: #0F0E17; }
    .status-limit  { background: #FF4365; color: #FFFFFE; }

    @media (max-width: 768px) {
        .gradient-title { font-size: 1.8em; }
        .welcome-header { font-size: 1.8em; }
    }

    hr {
        border-color: #9D4EDD;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ⚙️ CONFIG
# ============================================================
FREE_DAILY_LIMIT = 5
PREMIUM_DAILY_LIMIT = 100
PREMIUM_PRICE = "$4.99/month"
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/YOUR_PAYMENT_LINK"
ADMIN_PASSWORD = "admin123"  # Change this to something secure!
SUPPORT_EMAIL = "your-email@example.com"

DEMO_REPLIES = [
    "That's a fascinating question! 🌟 Let me think...",
    "I love that perspective! ✨ Here's my take...",
    "Great point! 🎨 In my view, it depends on context.",
    "Ooh, interesting! 🚀 Let's explore that.",
    "Wonderful question! 🌈 The short answer: it's nuanced.",
    "Excellent! 🎯 Let's break it down.",
]

# ============================================================
# 📊 USER TRACKING FUNCTIONS
# ============================================================

def get_analytics_db():
    """Get analytics database from session"""
    if "analytics_db" not in st.session_state:
        st.session_state.analytics_db = {
            "users": {},
            "sessions": [],
        }
    return st.session_state.analytics_db

def log_user_activity(username, action, query=None):
    """Log user activity to analytics"""
    analytics = get_analytics_db()
    timestamp = datetime.now()
    
    # Track user session
    if username not in analytics["users"]:
        analytics["users"][username] = {
            "first_login": timestamp.isoformat(),
            "last_login": timestamp.isoformat(),
            "total_messages": 0,
            "total_searches": [],
            "session_count": 0,
        }
    
    analytics["users"][username]["last_login"] = timestamp.isoformat()
    
    # Track individual session
    session_log = {
        "username": username,
        "timestamp": timestamp.isoformat(),
        "action": action,
        "query": query,
    }
    
    analytics["sessions"].append(session_log)
    
    if action == "message":
        analytics["users"][username]["total_messages"] += 1
        if query:
            analytics["users"][username]["total_searches"].append({
                "query": query,
                "timestamp": timestamp.isoformat()
            })

def get_session_start_time():
    """Get when user started current session"""
    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()
    return st.session_state.session_start

def get_session_duration():
    """Calculate session duration in minutes"""
    start = get_session_start_time()
    duration = (datetime.now() - start).total_seconds() / 60
    return round(duration, 1)

# ============================================================
# 🔐 AUTHENTICATION FUNCTIONS
# ============================================================

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_users_db():
    """Get users from session"""
    if "users_db" not in st.session_state:
        st.session_state.users_db = {
            "demo": {
                "is_premium": False,
                "created": "2026-01-01",
                "auth_method": "modern",
            }
        }
    return st.session_state.users_db

def register_user(username, password):
    """Register new user"""
    users = get_users_db()
    
    if username in users:
        return False, "Username already exists"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    users[username] = {
        "password": hash_password(password),
        "is_premium": False,
        "created": str(date.today()),
        "auth_method": "traditional",
    }
    return True, "Account created! Please log in."

def login_user(username, password):
    """Login user"""
    users = get_users_db()
    
    if username not in users:
        return False, "Username not found"
    
    if users[username]["password"] != hash_password(password):
        return False, "Incorrect password"
    
    return True, "Login successful!"

# ============================================================
# 🔐 SESSION STATE
# ============================================================
def init_session():
    today = str(date.today())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "msg_count_date" not in st.session_state or st.session_state.msg_count_date != today:
        st.session_state.msg_count_date = today
        st.session_state.msg_count_today = 0

    if "is_premium" not in st.session_state:
        st.session_state.is_premium = False

    if "username" not in st.session_state:
        st.session_state.username = None

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    if "openai_client" not in st.session_state:
        api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
        st.session_state.openai_client = OpenAI(api_key=api_key) if api_key else None

    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-4o-mini"

init_session()

# ============================================================
# 🎨 LOGIN PAGE
# ============================================================
if not st.session_state.logged_in:
    st.markdown('<div class="gradient-title">🌌 COSMOS 🌌</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Sign in to start chatting</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        # Admin Login Option
        admin_mode = st.checkbox("🔐 Admin Login")
        
        if admin_mode:
            st.subheader("Admin Dashboard")
            admin_pass = st.text_input("Admin Password", type="password", key="admin_pass")
            
            if st.button("🔐 Login as Admin", use_container_width=True):
                if admin_pass == ADMIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.is_admin = True
                    st.session_state.username = "ADMIN"
                    st.success("✅ Admin logged in!")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password")
        else:
            st.markdown("### 🔐 Sign In")
            
            if st.button("🌐 Sign in with Google", use_container_width=True, key="google_signin"):
                st.info("📧 Google Sign-In: Please enter your Google email and verify with Google OAuth")
                google_email = st.text_input("Google Email", key="google_email_input", placeholder="your.email@gmail.com")
                
                if google_email and "@" in google_email:
                    st.warning("⚠️ Note: In production, this will redirect to Google OAuth login")
                    if st.button("✅ Continue with Google", use_container_width=True):
                        users = get_users_db()
                        username, email = google_login(google_email)
                        st.session_state.logged_in = True
                        st.session_state.username = google_email
                        st.session_state.is_premium = users.get(google_email, {}).get("is_premium", False)
                        log_user_activity(google_email, "login", "google_signin")
                        st.success(f"✅ Signed in as {google_email}!")
                        st.rerun()
            
            st.markdown("**OR**")
            
            tab1, tab2 = st.tabs(["🔓 Login", "✍️ Register"])
            
            with tab1:
                st.subheader("Login with Email")
                
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("🚀 Login", use_container_width=True):
                    success, message = login_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        users = get_users_db()
                        st.session_state.is_premium = users[username].get("is_premium", False)
                        log_user_activity(username, "login")
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            with tab2:
                st.subheader("Create Account")
                
                new_username = st.text_input("Choose Username", key="register_username")
                new_password = st.text_input("Choose Password", type="password", key="register_password")
                new_password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")
                
                if st.button("✍️ Register", use_container_width=True):
                    if new_password != new_password_confirm:
                        st.error("Passwords don't match!")
                    else:
                        success, message = register_user(new_username, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.caption("🔒 Your data is secure. We never share your information.")

# ============================================================
# 📊 ADMIN DASHBOARD WITH CHAT
# ============================================================
elif st.session_state.is_admin:
    st.markdown(f'<div class="welcome-header">Welcome, ADMIN! 👑</div>', unsafe_allow_html=True)
    
    # Create tabs for Admin Controls and Chat
    tab_admin, tab_chat = st.tabs(["📊 Analytics", "💬 Chat"])
    
    with tab_admin:
        analytics = get_analytics_db()
        
        with st.sidebar:
            st.markdown("### 👑 ADMIN")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        
        # Overview stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(analytics["users"]))
        
        with col2:
            st.metric("Total Sessions", len(analytics["sessions"]))
        
        with col3:
            total_messages = sum(u["total_messages"] for u in analytics["users"].values())
            st.metric("Total Messages", total_messages)
        
        with col4:
            st.metric("Premium Users", 0)
        
        st.divider()
        
        # User activity table
        st.subheader("📋 Activity Log")
        
        if analytics["sessions"]:
            df_sessions = pd.DataFrame(analytics["sessions"])
            df_sessions["timestamp"] = pd.to_datetime(df_sessions["timestamp"])
            df_sessions = df_sessions.sort_values("timestamp", ascending=False)
            
            st.dataframe(
                df_sessions,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No user activity yet")
        
        st.divider()
        
        # User details
        st.subheader("👥 User Details")
        
        if analytics["users"]:
            for username, user_data in analytics["users"].items():
                with st.expander(f"👤 {username}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Messages", user_data["total_messages"])
                    
                    with col2:
                        st.metric("First Login", user_data["first_login"][:10])
                    
                    with col3:
                        st.metric("Last Login", user_data["last_login"][:10])
                    
                    st.write("**Search History:**")
                    if user_data["total_searches"]:
                        for search in user_data["total_searches"]:
                            st.caption(f"🔍 {search['query']} - {search['timestamp'][:10]}")
                    else:
                        st.caption("No searches yet")
        else:
            st.info("No users yet")
    
    with tab_chat:
        # Normal chat interface for admin
        with st.sidebar:
            st.markdown("### 👑 ADMIN (Chat Mode)")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        
        st.subheader("💬 Chat as Admin")
        
        if not st.session_state.messages:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    "Hello Admin! 👋\n\n"
                    "Test the Cosmos chatbot here.\n\n"
                    "Ask me anything! ✨"
                )

        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        prompt = None
        if "surprise" in st.session_state:
            prompt = st.session_state.surprise
            del st.session_state.surprise

        user_input = st.chat_input("💬 Type your message…")
        if user_input:
            prompt = user_input

        if prompt:
            log_user_activity("ADMIN", "message", prompt)

            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()

                if st.session_state.openai_client:
                    try:
                        with st.spinner("🤔 Thinking..."):
                            response = st.session_state.openai_client.chat.completions.create(
                                model=st.session_state.selected_model,
                                messages=st.session_state.messages,
                                max_tokens=1024,
                            )
                            reply = response.choices[0].message.content
                    except Exception as e:
                        reply = f"❌ Error: {str(e)[:120]}\n\nFalling back: {random.choice(DEMO_REPLIES)}"
                else:
                    reply = random.choice(DEMO_REPLIES) + f"\n\nYou said: \"{prompt[:60]}...\""

                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            st.rerun()

# ============================================================
# 💬 MAIN APP (if logged in and not admin)
# ============================================================
else:
    st.markdown(f'<div class="welcome-header">Welcome, {st.session_state.username}! 👋</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        
        if st.session_state.is_premium:
            st.markdown('<span class="status-pill status-premium">⭐ PREMIUM USER</span>', unsafe_allow_html=True)
            limit = PREMIUM_DAILY_LIMIT
        else:
            st.markdown('<span class="status-pill status-free">🆓 FREE TIER</span>', unsafe_allow_html=True)
            limit = FREE_DAILY_LIMIT

        used = st.session_state.msg_count_today
        remaining = max(0, limit - used)
        st.progress(min(used / limit, 1.0))
        st.markdown(f"**{remaining} / {limit}** messages left today")
        
        # Session duration
        duration = get_session_duration()
        st.caption(f"⏱️ Session time: {duration} min")

        if remaining == 0 and not st.session_state.is_premium:
            st.markdown(
                f'<div class="premium-banner">🚀 Daily limit reached!<br>'
                f'Upgrade to Premium for unlimited chats — {PREMIUM_PRICE}</div>',
                unsafe_allow_html=True
            )
            st.link_button("⭐ Upgrade Now", STRIPE_PAYMENT_LINK, use_container_width=True)

        st.divider()

        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        if st.button("✨ Surprise Me", use_container_width=True):
            prompts = [
                "Tell me a fun fact about space 🚀",
                "Give me a productivity tip ✨",
                "Tell me a short, uplifting story 🌟",
                "What 3 colors pair beautifully?",
                "Explain quantum computing simply 🔬",
                "Suggest a creative weekend project 🎨",
            ]
            st.session_state.surprise = random.choice(prompts)

        st.divider()

        if st.session_state.is_premium:
            model_choice = st.selectbox(
                "🤖 AI Model",
                ["gpt-4o-mini (Fast)", "gpt-4o (Smartest)", "gpt-3.5-turbo (Fastest)"]
            )
            st.session_state.selected_model = model_choice.split(" ")[0]
        else:
            st.markdown("🤖 **Model:** GPT-4o Mini")
            st.caption("⭐ Premium unlocks GPT-4o & GPT-3.5")

        st.divider()

        if st.session_state.openai_client:
            st.success("🟢 AI Connected")
        else:
            st.warning("🟡 Demo Mode (no API key)")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.rerun()

        st.caption(f"Need help? {SUPPORT_EMAIL}")

    # Chat area
    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(
                f"Hey **{st.session_state.username}**! 👋\n\n"
                f"I'm your colorful AI companion.\n\n"
                f"Ask me anything — about ideas, code, life, or the universe.\n\n"
                f"Try the **Surprise Me** button in the sidebar! ✨"
            )

    for msg in st.session_state.messages:
        avatar = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    prompt = None
    if "surprise" in st.session_state:
        prompt = st.session_state.surprise
        del st.session_state.surprise

    user_input = st.chat_input("💬 Type your message…")
    if user_input:
        prompt = user_input

    # Process message
    if prompt:
        limit = PREMIUM_DAILY_LIMIT if st.session_state.is_premium else FREE_DAILY_LIMIT
        if st.session_state.msg_count_today >= limit and not st.session_state.is_premium:
            st.error(
                f"🚫 You've hit your daily limit of {FREE_DAILY_LIMIT} messages. "
                f"Upgrade to Premium for unlimited chats!"
            )
            st.link_button(f"⭐ Upgrade for {PREMIUM_PRICE}", STRIPE_PAYMENT_LINK)
            st.stop()

        # Log the user message
        log_user_activity(st.session_state.username, "message", prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()

            if st.session_state.openai_client:
                try:
                    with st.spinner("🤔 Thinking..."):
                        response = st.session_state.openai_client.chat.completions.create(
                            model=st.session_state.selected_model,
                            messages=st.session_state.messages,
                            max_tokens=1024,
                        )
                        reply = response.choices[0].message.content
                except Exception as e:
                    reply = f"❌ Error: {str(e)[:120]}\n\nFalling back: {random.choice(DEMO_REPLIES)}"
            else:
                reply = random.choice(DEMO_REPLIES) + f"\n\nYou said: \"{prompt[:60]}...\""

            placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.msg_count_today += 1

        st.rerun()