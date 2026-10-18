import os
import time
import requests
import threading
from datetime import datetime, timedelta
import pytz
import random
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return "Enoch Strategy Bot is Running! 24/7 Live"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
        print("Sent")
    except Exception as e:
        print(e)

def get_signal():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/EUR", timeout=10).json()
        eur_usd = r['rates']['USD']
        last = eur_usd + random.uniform(-0.0003, 0.0003)
        sec = datetime.now().second
        if sec % 2 == 0:
            return "UP", last
        else:
            return "DOWN", last
    except:
        return random.choice([("UP", 1.0850), ("DOWN", 1.0850)])

def bot_loop():
    print("Bot don start... E dey road now!")
    while True:
        now_wat = datetime.now(WAT)
        result = get_signal()
        direction, price = result
        entry_dt = now_wat + timedelta(minutes=2)
        entry_str = entry_dt.strftime("%I:%M %p")
        icon = "🟢" if direction == "UP" else "🔴"
        
        msg1 = "🚀 <b>ENOCH STRATEGY</b> 🚀\n\n" + f"Pair: <b>EUR/USD</b>\nEntry: <b>{entry_str} WAT</b>\nPrice: {price:.5f}\n\nDirection in 1 min..."
        send(msg1)
        time.sleep(60)
        
        msg2 = "✅ <b>CONFIRMED</b> ✅\n\n" + f"EUR/USD\nEntry: {entry_str} WAT\nDirection: <b>{direction} {icon}</b>\n\nExpiry: 2 Min"
        send(msg2)
        time.sleep(600)

# Start Flask in background to keep Render happy (FREE)
threading.Thread(target=run_flask, daemon=True).start()
# Start Bot Loop
bot_loop()
