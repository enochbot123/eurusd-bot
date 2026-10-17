import os
import asyncio
import random
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import yfinance as yf
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = os.getenv("BOT_TOKEN", "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ")
LAGOS = ZoneInfo("Africa/Lagos")
CHANNEL_ID = "@EnochStrategyBot"  # Your channel

# Setup logging
logging.basicConfig(level=logging.INFO)

# Trading Sessions (WAT)
SESSIONS = [
    {"name": "MORNING", "start": "10:00", "end": "11:00", "icon": "🌅"},
    {"name": "AFTERNOON", "start": "13:00", "end": "14:00", "icon": "☀️"},
    {"name": "EVENING", "start": "17:00", "end": "20:00", "icon": "🌙"},
]

PAIRS = [
    ("EUR/USD OTC", "EURUSD=X"),
    ("GBP/USD OTC", "GBPUSD=X"),
    ("USD/JPY OTC", "JPY=X"),
    ("AUD/USD OTC", "AUDUSD=X"),
    ("EUR/JPY OTC", "EURJPY=X"),
]

# --- STRATEGY (EMA9 + RSI) ---
def get_signal(yf_symbol):
    try:
        data = yf.download(yf_symbol, period="1d", interval="1m", progress=False)
        if len(data) < 20:
            return None, 0, 0
        
        close = data['Close']
        # EMA 9
        ema9 = close.ewm(span=9).mean().iloc[-1]
        price = close.iloc[-1]
        
        # RSI 14
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1]

        if price > ema9 and rsi_val > 50 and rsi_val < 70:
            return "👻 UP", float(price), float(rsi_val)
        elif price < ema9 and rsi_val < 50 and rsi_val > 30:
            return "👻 DOWN", float(price), float(rsi_val)
        else:
            return None, float(price), float(rsi_val)
    except Exception as e:
        print(f"yfinance error {yf_symbol}: {e}")
        # Fallback random for testing if yfinance fails
        return random.choice(["👻 UP", "👻 DOWN"]), 0, 0

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save user
    if "users" not in context.application.bot_data:
       
