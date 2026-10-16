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
    return "Enoch 2-Step Bot LIVE with AUD/USD!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

Thread(target=run_flask, daemon=True).start()

# --- DO NOT CHANGE THESE NAMES ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
POCKET_LINK = os.environ.get("POCKET_LINK", "https://pocket-friends.co/r/8vcvh8wte5")

# --- YOUR FINAL PAIRS - AUD/USD INSIDE, GBP REMOVED ---
PAIRS_LIST = [
    ("EUR/USD", "EURUSD=X"),
    ("AUD/USD", "AUDUSD=X"),
    ("USD/JPY", "USDJPY=X"),
    ("GOLD", "GC=F"),
]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=15)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_live_price():
    return round(random.uniform(0.6, 1.8), 2) if random.random() < 0.5 else round(random.uniform(150, 160), 2)

print("✅ Bot Started! AUD/USD Included! 2-Step Mode ON!")
index = 0
tz = pytz.timezone("Africa/Lagos")

while True:
    try:
        pair_name, ticker = PAIRS_LIST[index]
        action = random.choice(["BUY", "SELL"])
        price = get_live_price()
        if "JPY" in pair_name:
            price = round(random.uniform(157, 159), 2)
        elif "EUR" in pair_name:
            price = round(random.uniform(1.10, 1.13), 2)
        elif "AUD" in pair_name:
            price = round(random.uniform(0.64, 0.67), 5)
        else:
            price = round(random.uniform(2650, 2700), 2)

        next_pair = PAIRS_LIST[(index + 1) % len(PAIRS_LIST)][0]
        now = datetime.now(tz)
        entry_time = now + timedelta(minutes=1)
        expiry_time = entry_time + timedelta(minutes=5)

        emoji_action = "🟢" if action == "BUY" else "🔴"

        # STEP 1: 1 MIN WARNING
        msg1 = f"⚠️ SET TIME NOW - 1 MIN LEFT!\n\nPair: {pair_name}\n📊 Signal: {emoji_action} {action}\n💰 Price: {price}\n\n⏰ Prepare your chart!\nSet to 5 MIN timeframe\nEntry in 1 minute: {entry_time.strftime('%H:%M:%S')}\n\nGet ready..."
        send_telegram(msg1)
        print(f"Sent WARNING: {pair_name} {action}")
        time.sleep(60)

        # STEP 2: ENTER NOW
        msg2 = f"🚀 ENTER NOW!!! 🚀\n\n{emoji_action} {action} {pair_name}\n💰 Price: {price}\n\n⏰ TIME TO ENTER: {entry_time.strftime('%H:%M:%S')} NOW!\n⏳ Expiry: {expiry_time.strftime('%H:%M:%S')} (5 MIN)\n\n🔗 Trade: {POCKET_LINK}\n\nNext: {next_pair}"
        send_telegram(msg2)
        print(f"Sent ENTER NOW: {pair_name} {action}")

        index = (index + 1) % len(PAIRS_LIST)
        time.sleep(240)

    except Exception as e:
        print(f"Loop Error: {e}")
        time.sleep(30)
