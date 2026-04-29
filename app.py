"""
🌌 COSMOS - AI Chat Platform with Database 🌌
A beautiful, vibrant AI chatbot interface with persistent user storage.

Features:
  - Beautiful neon dark theme
  - OpenAI GPT integration
  - GOOGLE SIGN-IN + Traditional Login
  - USER ANALYTICS (who signed in, what they searched, time spent)
  - SQLite DATABASE for persistent user storage
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
import sqlite3
import json

load_dotenv()

# ============================================================
# 💾 DATABASE SETUP
# ============================================================

DB_FILE = "cosmos_users.db"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT,
        is_premium INTEGER DEFAULT 0,
        auth_method TEXT DEFAULT 'traditional',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    
    # User activity table
    c.execute('''CREATE TABLE IF NOT EXISTS activity (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        query TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')
    
    # User messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (username) REFERENCES users(username)
    )''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user_db(username, password, email=None):
    """Register user in database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return False, "Username already exists"
        
        hashed_pwd = hash_password(password)
        c.execute("""INSERT INTO users (username, password, email, auth_method) 
                     VALUES (?, ?, ?, ?)""", 
                  (username, hashed_pwd, email, "traditional"))
        conn.commit()
        conn.close()
        return True, "Account created! Please log in."
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user_db(username, password):
    """Login user from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        hashed_pwd = hash_password(password)
        c.execute("SELECT username, is_premium FROM users WHERE username = ? AND password = ?", 
                  (username, hashed_pwd))
        result = c.fetchone()
        
        if result:
            # Update last login
            c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            return True, result[1]  # Return is_premium status
        else:
            conn.close()
            return False, None
    except Exception as e:
        return False, None

def google_login_db(email):
    """Google login - create or get user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        username = email.split("@")[0]
        
        c.execute("SELECT username, is_premium FROM users WHERE email = ?", (email,))
        result = c.fetchone()
        
        if not result:
            hashed_pwd = hash_password("google_oauth")
            c.execute("""INSERT INTO users (username, password, email, auth_method) 
                         VALUES (?, ?, ?, ?)""", 
                      (email, hashed_pwd, email, "google"))
            conn.commit()
            return email, False
        else:
            # Update last login
            c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?", (email,))
            conn.commit()
            return result[0], result[1]
    except Exception as e:
        return None, None
    finally:
        conn.close()

def log_activity_db(username, action, query=None):
    """Log user activity to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO activity (username, action, query) 
                     VALUES (?, ?, ?)""", 
                  (username, action, query))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def get_all_users():
    """Get all users from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT username, email, is_premium, created_at, last_login FROM users")
        users = c.fetchall()
        conn.close()
        return users
    except:
        return []

def get_user_activity(username):
    """Get user activity from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""SELECT action, query, timestamp FROM activity 
                     WHERE username = ? ORDER BY timestamp DESC""", (username,))
        activities = c.fetchall()
        conn.close()
        return activities
    except:
        return []

def get_all_activity():
    """Get all activity from database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""SELECT username, action, query, timestamp FROM activity 
                     ORDER BY timestamp DESC LIMIT 500""")
        activities = c.fetchall()
        conn.close()
        return activities
    except:
        return []

# Initialize database on startup
init_database()

# ============================================================
# 📱 PAGE CONFIG
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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background: linear-gradient(135deg, #0F0E17 0%, #1A1825 100%);
    }

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

    [data-testid="stSidebar"] {
        background-color: #1A1825 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFE; }

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
        padding: 10px 20px;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #9D4EDD 0%, #4CC9F0 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(157, 78, 221, 0.4);
    }

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

    @media (max-width: 768px) {
        .gradient-title { font-size: 1.8em; }
        .welcome-header { font-size: 1.8em; }
    }

    hr { border-color: #9D4EDD; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# ⚙️ CONFIG
# ============================================================
FREE_DAILY_LIMIT = 5
PREMIUM_DAILY_LIMIT = 100
PREMIUM_PRICE = "$4.99/month"
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/YOUR_PAYMENT_LINK"
ADMIN_PASSWORD = "admin123"
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

    if "session_start" not in st.session_state:
        st.session_state.session_start = datetime.now()

init_session()

def get_session_duration():
    """Calculate session duration in minutes"""
    start = st.session_state.session_start
    duration = (datetime.now() - start).total_seconds() / 60
    return round(duration, 1)

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
                    log_activity_db("ADMIN", "login")
                    st.success("✅ Admin logged in!")
                    st.rerun()
                else:
                    st.error("❌ Invalid admin password")
        else:
            st.markdown("### 🔐 Sign In")
            
            if st.button("🌐 Sign in with Google", use_container_width=True, key="google_signin"):
                st.info("📧 Google Sign-In: Please enter your Google email")
                google_email = st.text_input("Google Email", key="google_email_input", placeholder="your.email@gmail.com")
                
                if google_email and "@" in google_email:
                    st.warning("⚠️ Note: In production, this will redirect to Google OAuth login")
                    if st.button("✅ Continue with Google", use_container_width=True):
                        username, is_premium = google_login_db(google_email)
                        if username:
                            st.session_state.logged_in = True
                            st.session_state.username = google_email
                            st.session_state.is_premium = is_premium
                            log_activity_db(google_email, "login", "google_signin")
                            st.success(f"✅ Signed in as {google_email}!")
                            st.rerun()
                        else:
                            st.error("Error with Google login")
            
            st.markdown("**OR**")
            
            tab1, tab2 = st.tabs(["🔓 Login", "✍️ Register"])
            
            with tab1:
                st.subheader("Login with Email")
                
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                if st.button("🚀 Login", use_container_width=True):
                    success, is_premium = login_user_db(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.is_premium = is_premium
                        log_activity_db(username, "login")
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            with tab2:
                st.subheader("Create Account")
                
                new_username = st.text_input("Choose Username", key="register_username")
                new_email = st.text_input("Email (optional)", key="register_email")
                new_password = st.text_input("Choose Password", type="password", key="register_password")
                new_password_confirm = st.text_input("Confirm Password", type="password", key="register_password_confirm")
                
                if st.button("✍️ Register", use_container_width=True):
                    if new_password != new_password_confirm:
                        st.error("Passwords don't match!")
                    else:
                        success, message = register_user_db(new_username, new_password, new_email if new_email else None)
                        if success:
                            st.success(message)
                            log_activity_db(new_username, "register")
                        else:
                            st.error(message)
        
        st.markdown("---")
        st.caption("🔒 Your data is secure and stored in our database.")

# ============================================================
# 📊 ADMIN DASHBOARD
# ============================================================
elif st.session_state.is_admin:
    st.markdown(f'<div class="welcome-header">Welcome, ADMIN! 👑</div>', unsafe_allow_html=True)
    
    tab_admin, tab_chat = st.tabs(["📊 Analytics", "💬 Chat"])
    
    with tab_admin:
        with st.sidebar:
            st.markdown("### 👑 ADMIN")
            if st.button("🚪 Logout", use_container_width=True, key="admin_logout_1"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        
        # Overview stats
        all_users = get_all_users()
        all_activity = get_all_activity()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(all_users))
        
        with col2:
            st.metric("Total Activities", len(all_activity))
        
        with col3:
            premium_count = sum(1 for user in all_users if user[2] == 1)
            st.metric("Premium Users", premium_count)
        
        with col4:
            st.metric("Free Users", len(all_users) - premium_count)
        
        st.divider()
        
        # Activity log
        st.subheader("📋 Recent Activity")
        
        if all_activity:
            df_activity = pd.DataFrame(all_activity, columns=["Username", "Action", "Query", "Timestamp"])
            st.dataframe(df_activity, use_container_width=True, hide_index=True)
        else:
            st.info("No activity yet")
        
        st.divider()
        
        # User details
        st.subheader("👥 All Users")
        
        if all_users:
            df_users = pd.DataFrame(all_users, columns=["Username", "Email", "Premium", "Created", "Last Login"])
            st.dataframe(df_users, use_container_width=True, hide_index=True)
        else:
            st.info("No users yet")
    
    with tab_chat:
        with st.sidebar:
            st.markdown("### 👑 ADMIN (Chat Mode)")
            if st.button("🚪 Logout", use_container_width=True, key="admin_logout_2"):
                st.session_state.logged_in = False
                st.session_state.is_admin = False
                st.rerun()
        
        st.subheader("💬 Chat as Admin")
        
        if not st.session_state.messages:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("Hello Admin! 👋\n\nTest the Cosmos chatbot here. Ask me anything! ✨")

        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        user_input = st.chat_input("💬 Type your message…")
        if user_input:
            log_activity_db("ADMIN", "message", user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)

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
                        reply = f"❌ Error: {str(e)[:120]}"
                else:
                    reply = random.choice(DEMO_REPLIES)

                placeholder.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

            st.rerun()

# ============================================================
# 💬 MAIN APP (User Chat)
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
            st.caption("⭐ Premium unlocks more models")

        st.divider()

        if st.session_state.openai_client:
            st.success("🟢 AI Connected")
        else:
            st.warning("🟡 Demo Mode")

        st.divider()

        if st.button("🚪 Logout", use_container_width=True, key="user_logout"):
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

        log_activity_db(st.session_state.username, "message", prompt)

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