

import os
import random
from datetime import datetime, date
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(
    page_title="Colorful AI Chat ✨",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)
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

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A1825 !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFE; }

    /* Chat messages — User (purple bubble) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, #9D4EDD 0%, #7B2FBF 100%) !important;
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(157, 78, 221, 0.3);
    }

    /* Chat messages — Assistant (blue bubble) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
        border-radius: 18px !important;
        padding: 14px 18px !important;
        margin: 8px 0 !important;
        box-shadow: 0 4px 12px rgba(30, 136, 229, 0.3);
    }

    /* Make chat text white */
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

    /* Mobile-friendly: make text bigger on small screens */
    @media (max-width: 768px) {
        .gradient-title { font-size: 1.8em; }
    }
</style>
""", unsafe_allow_html=True)
FREE_DAILY_LIMIT = 5            # Free users: messages per day
PREMIUM_DAILY_LIMIT = 100       # Premium users: messages per day
PREMIUM_PRICE = "$4.99/month"   
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/YOUR_PAYMENT_LINK"  # Replace after Stripe setup
APP_NAME = "Colorful AI Chat"
SUPPORT_EMAIL = "your-email@example.com"  # Replace with yours

DEMO_REPLIES = [
    "That's a fascinating question! 🌟 Let me think...",
    "I love that perspective! ✨ Here's my take...",
    "Great point! 🎨 In my view, it depends on context.",
    "Ooh, interesting! 🚀 Let's explore that.",
    "Wonderful question! 🌈 The short answer: it's nuanced.",
    "Excellent! 🎯 Let's break it down.",
]
def init_session():
    today = str(date.today())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "msg_count_date" not in st.session_state or st.session_state.msg_count_date != today:
        st.session_state.msg_count_date = today
        st.session_state.msg_count_today = 0

    # Premium status (in real app, check from database)
    if "is_premium" not in st.session_state:
        st.session_state.is_premium = False

    # OpenAI client
    if "openai_client" not in st.session_state:
        api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
        st.session_state.openai_client = OpenAI(api_key=api_key) if api_key else None
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gpt-4o-mini"
init_session()
st.markdown('<div class="gradient-title">✨ COLORFUL AI CHAT ✨</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your vibrant AI companion — powered by Python &amp; OpenAI</div>', unsafe_allow_html=True)
with st.sidebar:
    st.markdown("### 🎨 Menu")

    # Status pill
    if st.session_state.is_premium:
        st.markdown('<span class="status-pill status-premium">⭐ PREMIUM USER</span>', unsafe_allow_html=True)
        limit = PREMIUM_DAILY_LIMIT
    else:
        st.markdown('<span class="status-pill status-free">🆓 FREE TIER</span>', unsafe_allow_html=True)
        limit = FREE_DAILY_LIMIT

    # Usage counter
    used = st.session_state.msg_count_today
    remaining = max(0, limit - used)
    st.progress(min(used / limit, 1.0))
    st.markdown(f"**{remaining} / {limit}** messages left today")

    if remaining == 0 and not st.session_state.is_premium:
        st.markdown(
            f'<div class="premium-banner">🚀 Daily limit reached!<br>'
            f'Upgrade to Premium for unlimited chats — {PREMIUM_PRICE}</div>',
            unsafe_allow_html=True
        )
        st.link_button("⭐ Upgrade Now", STRIPE_PAYMENT_LINK, use_container_width=True)

    st.divider()

    # New Chat
    if st.button("🆕 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Surprise prompt
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

    # Model selector (premium only)
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

    # API status
    if st.session_state.openai_client:
        st.success("🟢 AI Connected")
    else:
        st.warning("🟡 Demo Mode (no API key)")

    st.divider()

    # Footer
    st.caption(f"Need help? {SUPPORT_EMAIL}")
    st.caption("Built with ❤️ using Streamlit")

# ============================================================
# 💬 CHAT AREA
# ============================================================
# Show welcome message if no chat history
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(
            "Hello! 👋 I'm your colorful AI companion.\n\n"
            "Ask me anything — about ideas, code, life, or the universe.\n\n"
            "Try the **Surprise Me** button in the sidebar! ✨"
        )

# Render history
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Handle surprise prompt
prompt = None
if "surprise" in st.session_state:
    prompt = st.session_state.surprise
    del st.session_state.surprise

# Chat input
user_input = st.chat_input("💬 Type your message…")
if user_input:
    prompt = user_input

# ============================================================
# 🚀 PROCESS MESSAGE
# ============================================================
if prompt:
    # Check daily limit
    if st.session_state.msg_count_today >= limit and not st.session_state.is_premium:
        st.error(
            f"🚫 You've hit your daily limit of {FREE_DAILY_LIMIT} messages. "
            f"Upgrade to Premium for unlimited chats!"
        )
        st.link_button(f"⭐ Upgrade for {PREMIUM_PRICE}", STRIPE_PAYMENT_LINK)
        st.stop()

    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Generate AI response
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

    # Refresh sidebar counter
    st.rerun()
