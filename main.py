import os
import time
import random
import requests
import pytz
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch 2-Step Bot LIVE!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

# YOUR FINAL PAIRS - WITH AUD/USD
PAIRS_LIST = [
    ("EUR/USD OTC", "EURUSD=X"),
    ("AUD/USD OTC", "AUDUSD=X"),
    ("USD/JPY OTC", "USDJPY=X"),
    ("GOLD OTC", "GC=F"),
]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=15)
    except:
        pass

def get_signal(pair_name):
    action = random.choice(["BUY", "SELL"])
    price = round(random.uniform(0.65, 1.09), 5)
    return action, price

print("Bot FIXED! Now with AUD/USD and BUY/SELL")
index = 0
tz = pytz.timezone("Africa/Lagos")

while True:
    try:
        pair_name, ticker = PAIRS_LIST[index]
        action, price = get_signal(pair_name)
        next_pair = PAIRS_LIST[(index + 1) % len(PAIRS_LIST)][0]

        emoji = "🟢" if action == "BUY" else "🔴"
        msg = f"{emoji} {action} {pair_name}\nPrice: {price}\nExpiry: 5 mins\nNext: {next_pair}\nTime: {datetime.now(tz).strftime('%H:%M')}"

        print(msg)
        send_telegram(msg)

        index = (index + 1) % len(PAIRS_LIST)
        time.sleep(300)

    except Exception as e:
        print(e)
        time.sleep(30)
