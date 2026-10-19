# -*- coding: utf-8 -*-
import os, time, requests, threading, random
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
def home(): return "Enoch System LIVE - Final Code"
def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = reply_markup
    try: requests.post(url, json=data, timeout=15)
    except: pass

PAIRS = ["EUR/USD OTC","Gold OTC","USD/JPY OTC","AUD/USD OTC","EUR/JPY OTC","GBP/JPY OTC","USD/CAD OTC","EUR/GBP OTC","USD/CHF OTC","AUD/JPY OTC","EUR/AUD OTC","BTC/USD OTC","EUR/CAD OTC","NZD/USD OTC","Silver OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "✅ REGISTER HERE"}, {"text": "📊 My Trading ID"}],
        [{"text": "ℹ️ How it works"}, {"text": f"💬 Chat {MY_USERNAME}"}],
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
                name = from_user.get("first_name", "Trader")
                username = from_user.get("username", "No username")
