import os
import time
import requests
import threading
import random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
MY_ID = "8529194860"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return "Enoch Bot LIVE OK"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send(chat_id, text):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=15)
    except:
        pass

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD"]

def bot_loop():
    time.sleep(5)
    last = ""
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            if h == 10:
                sess = "MORNING"
            elif h == 13:
                sess = "AFTERNOON"
            elif h == 17:
                sess = "EVENING"
            else:
                time.sleep(30)
                continue
            pair = random.choice(PAIRS)
            if pair == last:
                pair = random.choice(PAIRS)
            last = pair
            direction = random.choice(["UP","DOWN"])
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            m1 = "Currency pair: " + pair + " | Expiration 3min | SET " + set_str + " | +92%"
            m2 = "Entry time: " + set_str + " " + sess + " | Direction: " + direction
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(240
