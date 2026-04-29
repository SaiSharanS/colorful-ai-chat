# ✨ Colorful AI Chat

A beautiful, vibrant AI chatbot built with Python, Streamlit & OpenAI.

🌐 **Live demo:** https://your-app.streamlit.app

## Features

- 🎨 Beautiful neon dark theme with animated gradients
- 💬 Real-time AI responses powered by OpenAI
- 📱 Mobile-responsive design
- 🆓 Free tier: 5 messages per day
- ⭐ Premium tier: Unlimited messages + GPT-4o access
- 🚀 Easy to deploy and customize

## Quick Start (Local)

```bash
# 1. Clone this repo
git clone https://github.com/YOUR_USERNAME/colorful-ai-chat.git
cd colorful-ai-chat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your OpenAI API key to a .env file
echo "OPENAI_API_KEY=sk-proj-your-key-here" > .env

# 4. Run!
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Sign in with GitHub
4. Click "New app" → select your repo → `app.py`
5. In **Advanced settings → Secrets**, add:
   ```
   OPENAI_API_KEY = "sk-proj-your-key-here"
   ```
6. Click **Deploy**

You'll get a public URL like `https://your-app.streamlit.app` 🎉

## Configuration

Edit the `CONFIG` section in `app.py`:

```python
FREE_DAILY_LIMIT = 5         # Free user limit
PREMIUM_DAILY_LIMIT = 100    # Premium limit
PREMIUM_PRICE = "$4.99/month"
STRIPE_PAYMENT_LINK = "https://buy.stripe.com/YOUR_LINK"
```

## Monetization Setup (Stripe)

1. Sign up at https://stripe.com
2. Create a Product → "Premium Subscription" → $4.99/month
3. Copy the **Payment Link**
4. Paste into `STRIPE_PAYMENT_LINK` in `app.py`

## License

MIT — free to use & modify.

## Support

Questions? Email your-email@example.com
