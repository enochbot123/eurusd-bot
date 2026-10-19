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
    html = "<html><head><meta charset='utf-8'><title>Enoch System Pro</title></head>"
    html += "<body style='background:#0a0a0a;color:#00ff88;text-align:center;padding-top:60px;font-family:Arial'>"
    html += "<h1>\U0001f680 Enoch System LIVE \U0001f680</h1>"
    html += "<h2>\U0001f4bc 5 Pairs Pro - Professional</h2>"
    html += "<p>\u2705 Status: ONLINE & ACTIVE</p>"
    html += "<p>\u23f0 Sessions: 10AM | 1PM | 5PM UTC</p>"
    html += "<p>\U0001f550 Reminders: 9:45AM | 12:45PM | 4:45PM</p>"
    html += "<p>\U0001f4ca Pairs: EUR/USD OTC, AUD/CAD OTC, AUD/JPY, CHF/JPY OTC, AUD/CAD (+92%)</p>"
    html += "<p>\U0001f525 Powered by @Enochsystem</p></body></html>"
    return html

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
        print(str(e))

# NEW 5 PAIRS FROM YOUR SCREENSHOT - ALL +92%
PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "\U0001f517 REGISTER HERE"}, {"text": "\U0001f194 My Trading ID"}],
        [{"text": "\u2139\ufe0f How it works"}, {"text": "\U0001f4ac Chat @Enochsystem"}],
        [{"text": "\U0001f680 Start Signals"}]
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
                first_name = from_user.get("first_name", "Trader")
                user_name = from_user.get("username", "No username")
                if not chat_id:
                    continue
                low = text.lower()
                if "/start" in low or "start signals" in low:
                    alert = "NEW PERSON Name: " + first_name + " Username: @" + user_name + " ID: " + str(chat_id)
                    send(MY_ID, alert)
                    welcome = "\U0001f680 <b>THIS IS NOT GAMBLING</b>\n\U0001f4bc <b>THIS IS STRATEGY</b>\n\nHello " + first_name + " \U0001f44b\n\nWelcome to <b>Enoch System Pro!</b> \u2728\n\n\U0001f4bc Professional Hub\n\U0001f4ca <b>5 Pairs Pro (+92% Payout)</b>\n\U0001f4b1 EUR/USD OTC\n\U0001f4b1 AUD/CAD OTC\n\U0001f4b1 AUD/JPY\n\U0001f4b1 CHF/JPY OTC\n\U0001f4b1 AUD/CAD\n\n\u23f0 Sessions: 10AM | 1PM | 5PM UTC\n\U0001f550 Reminders: 9:45AM, 12:45PM, 4:45PM\n\u2705 3Min Expiry | \U0001f525 Strategy\n\nUse buttons below \U0001f447"
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)
                if "how it works" in low:
                    txt = "\u2139\ufe0f <b>HOW IT WORKS - PRO</b>\n\n1\ufe0f\u20e3 REGISTER HERE \U0001f517\n2\ufe0f\u20e3 Fund $10 \U0001f4b5\n3\ufe0f\u20e3 Send screenshot \U0001f4f8\n4\ufe0f\u20e3 Get VIP \U0001f389\n\n\U0001f4ca 5 Pairs +92%:\nEUR/USD OTC, AUD/CAD OTC, AUD/JPY, CHF/JPY OTC, AUD/CAD\n\n\u23f0 Sessions: 10AM | 1PM | 5PM UTC"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                if "my trading id" in low:
                    txt = "\U0001f194 <b>Trading ID</b>\n\n1\ufe0f\u20e3 Login \U0001f510\n2\ufe0f\u20e3 Profile \U0001f464\n3\ufe0f\u20e3 Copy ID \U0001f4cb\n4\ufe0f\u20e3 Send to @Enochsystem \U0001f4ac"
                    send(chat_id, txt
