import os, random, threading
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ====== FIX RENDER PORT ERROR ======
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Enoch Professional System Running!"
def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
# ===================================

BOT_TOKEN = os.getenv("BOT_TOKEN").strip() if os.getenv("BOT_TOKEN") else None
if not BOT_TOKEN:
    print("❌ BOT_TOKEN MISSING!")
    exit(1)

REGISTER_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
CHANNEL_ID = -1003714315133
WAT = ZoneInfo("Africa/Lagos")

# BETTER PAIRS - MOVES WELL MORNING/AFTERNOON/NIGHT - NO GOLD, NO GBP/USD
PAIRS = ["EUR/USD", "USD/JPY", "EUR/JPY", "AUD/USD", "USD/CAD", "NZD/USD"]

# PROFESSIONAL ANALYSIS REASONS
REASONS = [
    {"setup": "Breakout + Retest", "why": "Price don break strong resistance for M15, now e dey retest am as new support. Volume confirm breakout."},
    {"setup": "Double Bottom Support", "why": "Market form double bottom for M5 support zone. RSI dey 32 (oversold) + Bullish engulfing candle."},
    {"setup": "Trend Continuation", "why": "Strong uptrend for H1, price dey bounce for EMA 50. Pullback done, continuation likely."},
    {"setup": "Resistance Rejection", "why": "Price hit strong supply zone for M15, wick rejection + Bearish pin bar. Sellers dey control."},
    {"setup": "Breakdown + Retest", "why": "Price breakdown from support for M15, retest as resistance with high volume. Bearish momentum."},
    {"setup": "Support Bounce + RSI", "why": "Price for major support, RSI divergence + bullish hammer candle for M5."},
]

def private_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER - POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("🆔 HOW TO GET TRADING ID", callback_data="howto")],
        [InlineKeyboardButton("📊 PROFESSIONAL SETTINGS", callback_data="settings")],
        [InlineKeyboardButton("📢 JOIN SIGNAL CHANNEL", url="https://t.me/+YOURCHANNEL")],
        [InlineKeyboardButton("💬 CONTACT ADMIN", url="https://t.me/Enochsystem")],
    ])

PRO_WELCOME = """⭐ ENOCH PROFESSIONAL SYSTEM ⭐
Powered by Enoch System

Hello {name} 👋

WELCOME TO PROFESSIONAL TRADING!

📊 PROFESSIONAL SETTINGS:
━━━━━━━━━━━━━━
⏰ SESSIONS: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ ENTRY: Next M1 Candle
⏱️ EXPIRY: 3 MINUTES [M3]
🎯 PAIRS: EUR/USD, USD/JPY, EUR/JPY, AUD/USD, USD/CAD, NZD/USD
📈 STRATEGY: Breakout + Retest + Volume + RSI
⚠️ RISK: 1% Per Trade | Martingale 1 Step ONLY
📊 CONFIDENCE: 88-96%

🔗 YOUR REGISTER LINK:
{link}

👇 CLICK BELOW TO START:
"""

HOW_TO_TEXT = """🆔 HOW TO GET YOUR TRADING ID:

1. Click REGISTER link above
2. Register account for Pocket Option
3. Go to Profile -> Trading ID
4. Copy your ID (e.g., 12345678)
5. Paste am here for this bot

✅ After you submit, you go start to receive PROFESSIONAL signals for channel!

Need help? Contact @Enochsystem
"""

SETTINGS_TEXT = """📊 ENOCH PROFESSIONAL SETTINGS:

🔹 TIMEFRAME ANALYSIS: M5, M15, H1
🔹 ENTRY: M1 Next Candle
🔹 EXPIRY: M3 (3 Minutes)
🔹 INDICATORS: EMA 50, RSI, Support/Resistance, Volume
🔹 RISK MANAGEMENT: 1% + 1 Martingale Step
🔹 SESSIONS: Best movement for these pairs:
   Morning (9:30 WAT): EUR/USD, EUR/JPY
   Afternoon (2:30 WAT): USD/JPY, USD/CAD
   Night (8:30 WAT): AUD/USD, NZD/USD

We dey analyze real market structure before we send signal!
"""

# ===== PRIVATE BOT =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PRO_WELCOME.format(name=update.effective_user.first_name, link=REGISTER_LINK), reply_markup=private_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "howto":
        await query.message.reply_text(HOW_TO_TEXT, reply_markup=private_menu())
    elif query.data == "settings":
        await query.message.reply_text(SETTINGS_TEXT, reply_markup=private_menu())

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader_id = update.message.text.strip()
    print(f"NEW ID: {update.effective_user.first_name} => {trader_id}")
    await update.message.reply_text(f"✅ PROFESSIONAL ID RECEIVED!\n\n🆔 ID: {trader_id}\nSaved! You go get signals for next session.\n\n{REGISTER_LINK}", reply_markup=private_menu())

# =====
