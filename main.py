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
MY_PRIVATE_ID = "8529194860"

WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Bot LIVE - Final Code"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(text):
    if not BOT_TOKEN:
        print("BOT_TOKEN missing!")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for chat_id in [CHANNEL_ID, MY_PRIVATE_ID]:
        try:
            r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
            print(f"Sent to {chat_id} -> {r.status_code}")
        except Exception as e:
            print(f"Error {chat_id}: {e}")

def get_analysis(direction):
    rsi = round(random.uniform(28, 72), 1)
    if direction == "UP":
        return random.choice([
            f"Price broke support with bullish momentum. RSI {rsi} shows buyers in control. Based on this, we enter a buy trade.",
            f"Bullish engulfing detected. RSI {rsi} confirms reversal. Buyers taking over.",
            f"Support holding firm. RSI {rsi} indicates uptrend continuation. We enter BUY."
        ])
    else:
        return random.choice([
            f"Price rejected at resistance with bearish momentum. RSI {rsi} shows sellers in control. Based on this, we enter a sell trade.",
            f"Double top formation. RSI {rsi} shows overbought. Sellers stepping in.",
            f"Shooting star at resistance. RSI {rsi} confirms downtrend. We enter SELL."
        ])

STRONG_PAIRS = [
    "EUR/USD OTC",
    "Gold OTC",
    "USD/JPY OTC",
    "AUD/USD OTC",
    "EUR/JPY OTC",
    "GBP/JPY OTC",
    "USD/CAD OTC",
    "EUR/GBP OTC",
    "USD/CHF OTC",
    "AUD/JPY OTC",
    "EUR/AUD OTC",
    "BTC/USD OTC",
    "EUR/CAD OTC",
    "NZD/USD OTC",
    "Silver OTC"
]

def bot_loop():
    print("Bot started - Final timing + bear emoji")
    last_pair = ""
    while True:
        now = datetime.now(WAT)

        # SYNC TIME - make e no rush, wait till new minute start
        if now.second != 0:
            time.sleep(60 - now.second)
            continue

        pair = random.choice(STRONG_PAIRS)
        while pair == last_pair:
            pair = random.choice(STRONG_PAIRS)
        last_pair = pair

        direction = random.choice(["UP", "DOWN"])
        
        # EMOJI - SECOND ONE WEY YOU CHOOSE = BEAR
        if direction == "UP":
            emoji = "👻"
        else:
            emoji = "🐻"

        set_dt = now + timedelta(minutes=1)
        set_str = set_dt.strftime("%H:%M")

        hour = set_dt.hour
        session = "MORNING" if 5 <= hour < 12 else "AFTERNOON" if 12 <= hour < 17 else "EVENING"

        reason = get_analysis(direction)
        short_name = pair.replace(" OTC","")

        msg1 = f"📊 Currency pair: {pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {set_str} - Prepare {short_name
