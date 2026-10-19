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
    return "Enoch System LIVE - 5 Pairs Fixed"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        pass

PAIRS = ["Gold OTC","EUR/USD OTC","GBP/USD OTC","EUR/JPY OTC","GBP/JPY OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "REGISTER HERE"}, {"text": "My Trading ID"}],
        [{"text": "How it works"}, {"text": "Chat @Enochsystem"}],
        [{"text": "Start Signals"}]
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
                chat_data = msg.get("chat", {})
                chat_id = chat_data.get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
                first_name = from_user.get("first_name", "Trader")
                user_name = from_user.get("username", "No username")
                if not chat_id:
                    continue
                low = text.lower()
                if "/start" in low or "start signals" in low:
                    alert = "NEW PERSON Name: " + first_name + " Username: @" + user_name + " ID: " + str(chat_id)
                    send(MY_ID, alert)
                    welcome = "THIS IS NOT GAMBLING THIS IS STRATEGY Hello " + first_name + " Welcome to Enoch System Professional Trading Hub 5 Pairs Pro System Sessions: 10AM | 1PM | 5PM UTC 3Min Expiry Use buttons below"
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)
                elif "how it works" in low:
                    txt = "HOW IT WORKS 1. Press REGISTER HERE 2. Fund $10 3. Send screenshot to @Enochsystem 4. Get VIP Channel 5 Pairs: Gold, EUR/USD, GBP/USD, EUR/JPY, GBP/JPY Sessions: 10AM | 1PM | 5PM UTC"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "my trading id" in low:
                    txt = "How to get Trading ID 1. Login Pocket Option 2. Go to Profile 3. Copy your ID 4. Send to @Enochsystem"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "register here" in low:
                    txt = "REGISTER HERE Use my official link: " + MY_LINK + " After register Fund $10 Send ID to @Enochsystem VIP access to 5 Pairs Pro"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "chat" in low:
                    send(chat_id, "Chat Admin: @Enochsystem He dey online!", reply_markup=PRO_KEYBOARD)
        except Exception:
           
