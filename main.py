import os
import time
import random
import requests
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

PAIRS_LIST = [
    ("EUR/USD OTC", "EURUSD=X"),
    ("AUD/USD OTC", "AUDUSD=X"),
    ("USD/JPY OTC", "USDJPY=X"),
    ("GOLD OTC", "GC=F"),
]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

print("Bot FIXED with AUD/USD")
idx = 0
while True:
    try:
        pair = PAIRS_LIST[idx][0]
        action = random.choice(["BUY", "SELL"])
        nxt = PAIRS_LIST[(idx+1) % len(PAIRS_LIST)][0]
        emoji = "🟢" if action == "BUY" else "🔴"
        msg = f"{emoji} {action} {pair}\nExpiry: 5 mins\nNext: {nxt}"
        print(msg)
        send_telegram(msg)
        idx = (idx + 1) % len(PAIRS_LIST)
        time.sleep(300)
    except Exception as e:
        print(e)
        time.sleep(30)
