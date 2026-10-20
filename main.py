import os, random
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REGISTER_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
CHANNEL_ID = "-1003714315133"
WAT = ZoneInfo("Africa/Lagos")

# PAIRS - GBP/USD & GOLD DON COMOT
PAIRS = ["EUR/USD", "USD/JPY", "EUR/JPY", "AUD/USD", "USD/CAD"]

# ===== PROFESSIONAL SETTINGS FOR PRIVATE BOT =====
def pro_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER - POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("📢 JOIN SIGNAL CHANNEL", url="https://t.me/+YOURCHANNEL")],
        [InlineKeyboardButton("🆔 SUBMIT TRADING ID", callback_data="submit")],
    ])

PRO_WELCOME = """⭐ ENOCH PROFESSIONAL SYSTEM ⭐
Powered by Enoch System

👋 Hello {name}!

📊 PROFESSIONAL SETTINGS:
━━━━━━━━━━━━
⏰ SESSIONS: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ EXPIRY: 3 MINUTES [M3]
📈 ENTRY: Next Candle M1
🎯 STRATEGY: Breakout + Retest + Volume Confirm
📊 CONFIDENCE: 89-96%
⚠️ RISK: 1% Per Trade | Martingale 1 Step Only

💱 PAIRS: EUR/USD, USD/JPY, EUR/JPY, AUD/USD, USD/CAD

🔗 YOUR LINK: {link}

👇 Click REGISTER to start, then submit your Trading ID!
"""

# ===== PRIVATE BOT HAND
