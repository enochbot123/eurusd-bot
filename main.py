import os, time, random, requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Bot V3 LIVE"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_flask, daemon=True).start()

TELEGRAM_TOKEN = "8529194860:AAEIYxCX"
TELEGRAM_CHAT_ID = "8868905914"
POCKET_LINK = "https://pocket-friends.com"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except Exception as e:
        print("Error:", e)

def make_signal():
    wat = pytz.timezone('Africa/Lagos')
    now = datetime.now(wat).strftime("%I:%M %p")
    pair = "EUR/USD"
    side = random.choice(["BUY 📈", "SELL 📉"])
    direction_text = "🐂 UP" if "BUY" in side else "🐻 DOWN"
    msg = f"""💰Currency pair: {pair}
Direction: {direction_text}

🔥 {pair} - {side}
⏰ Time: {now} (UTC+1)
⏳ Expiry: 1 Min
📊 Reason: Strong trend

👉 Trade here: {POCKET_LINK}

⚠️ Risk: 1-2% only"""
    return msg

send_telegram("✅ Enoch Bot V3 don start for Render FREE!")

while True:
    sig = make_signal()
    send_telegram(sig)
    time.sleep(60)
