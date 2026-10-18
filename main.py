# -*- coding: utf-8 -*-
import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
MY_ID = os.getenv("MY_ID", "8529194860")

WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Bot LIVE"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def send(text):
    if not BOT_TOKEN:
        print("BOT_TOKEN missing")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for cid in [CHANNEL_ID, MY_ID]:
        try:
            requests.post(url, json={"chat_id": cid, "text": text}, timeout=15)
            print(f"Sent to {cid}")
        except Exception as e:
            print(e)

def get_analysis(direction):
    rsi = round(random.uniform(28, 72), 1)
    if direction == "UP":
        return f"Price broke support with bullish momentum. RSI {rsi} shows buyers in control. Based on this, we enter a buy trade."
    else:
        return f"Price rejected at resistance with bearish momentum. RSI {rsi} shows sellers in control. Based on this, we enter a sell trade."

PAIRS = [
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
    print("Bot started - Clock Emoji Inside")
    last = ""
    while True:
        now = datetime.now(WAT)
        if now.second != 0:
            time.sleep(60 - now.second)
            continue

        pair = random.choice(PAIRS)
        while pair == last:
            pair = random.choice(PAIRS)
        last = pair

        direction = random.choice(["UP", "DOWN"])
        emoji = "👻" if direction == "UP" else "🐻"

        set_dt = now + timedelta(minutes=1)
        set_str = set_dt.strftime("%H:%M")

        hour = set_dt.hour
        if 5 <= hour < 12:
            session = "MORNING"
        elif 12 <= hour < 17:
            session = "AFTERNOON"
        else:
            session = "EVENING"

        reason = get_analysis(direction)
        short = pair.replace(" OTC","")

        # THIS ONE GET CLOCK EMOJI ⏰ INSIDE
        msg1 = f"📊 Currency pair: {pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {set_str} - Prepare {short}"
        msg2 = f"Entry time: ⏰ {set_str} - {session}\nDirection: {emoji} {direction}\n\n➤ {reason}"
        next_pair = random.choice(PAIRS)
        next_dt = set_dt + timedelta(minutes=5)
        next_str = next_dt.strftime("%H:%M")
        msg3 = f"❗ (UTC+1) - {session}\n\n📊 Currency pair: {next_pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {next_str} - Prepare {next_pair.replace(' OTC','')}"

        send(msg1)
        time.sleep(60)
        send(msg2)
        time.sleep(20)
        send(msg3)
        time.sleep(240)

threading.Thread(target=run_flask, daemon=True).start()
bot_loop()
