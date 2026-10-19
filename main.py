
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
MY_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Enoch System - Pro Bot</title></head>
    <body style='background:#0a0a0a;color:#00ff88;text-align:center;padding-top:60px;font-family:Arial'>
    <h1>🚀 Enoch System LIVE</h1>
    <h2>💼 5 Pairs Pro - Professional Trading Bot</h2>
    <p>✅ Status: ONLINE & ACTIVE</p>
    <p>⏰ Sessions: 10AM | 1PM | 5PM UTC</p>
    <p>🕐 Reminders: 9:45AM | 12:45PM | 4:45PM</p>
    <p>📊 Pairs: Gold, EUR/USD, GBP/USD, EUR/JPY, GBP/JPY</p>
    <p>⏳ Expiry: 3 Minutes | Strategy Based</p>
    <p style='margin-top:30px'>💬 Admin: @Enochsystem</p>
    </body>
    </html>
    """

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    payload = {}
    payload["chat_id"] = chat_id
    payload["text"] = text
    payload["parse_mode"] = "HTML"
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(e)

PAIRS = ["Gold OTC","EUR/USD OTC","GBP/USD OTC","EUR/JPY OTC","GBP/JPY OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "🔗 REGISTER HERE"}, {"text": "🆔 My Trading ID"}],
        [{"text": "ℹ️ How it works"}, {"text": "💬 Chat @Enochsystem"}],
        [{"text": "🚀 Start Signals"}]
    ],
    "resize_keyboard": True
}

def listen_commands():
    offset = 0
    base = "https://api.telegram.org/bot" + BOT_TOKEN + "/getUpdates"
    while True:
        try:
            r = requests.get(base, params={"offset": offset, "timeout": 30}, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_info = msg.get("chat", {})
                chat_id = chat_info.get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
               
