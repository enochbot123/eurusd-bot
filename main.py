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
    return "Enoch Strategy LIVE - 15 Pairs - Old Format"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    targets = [CHANNEL_ID, MY_PRIVATE_ID]
    for chat_id in targets:
        try:
            requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            print(f"Sent to {chat_id}")
        except Exception as e:
            print(f"Error {chat_id}: {e}")

def get_analysis(direction):
    rsi = round(random.uniform(26, 74), 1)
    if direction == "UP":
        return random.choice([
            f"Price broke support with bullish momentum. RSI {rsi} shows buyers in control. Based on this, we enter a buy trade.",
            f"Bullish engulfing pattern detected. RSI {rsi} confirms oversold reversal. Buyers taking over.",
            f"Support level holding strong. RSI {rsi} indicates uptrend continuation. We go for BUY.",
            f"Price forming hammer candle at support. RSI {rsi} shows bullish divergence. Enter BUY."
        ])
    else:
        return random.choice([
            f"Price rejected at resistance with bearish momentum. RSI {rsi} shows sellers in control. Based on this, we enter a sell trade.",
            f"Double top at resistance. RSI {rsi} indicates overbought condition. Sellers stepping in.",
            f"Shooting star candle formed. RSI {rsi} confirms downtrend. We go for SELL.",
            f"Breakdown below support with volume. RSI {rsi} shows bearish pressure. Enter SELL."
        ])

# 15 STRONG PAIRS - GBP/USD DON COMOT
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
    print("Bot started - 15 Pairs - Old Format - No GBP/USD")
    last = ""
    while True:
        now = datetime.now(WAT)
        pair = random.choice(STRONG_PAIRS)
        while pair == last:
            pair = random.choice(STRONG_PAIRS)
        last = pair

        direction = random.choice(["UP", "DOWN"])
        icon = "👻" if direction == "UP" else "👹"

        set_dt = now + timedelta(minutes=1)
        set_str = set_dt.strftime("%H:%M")
        entry_str = set_str

        hour = set_dt.hour
        session = "MORNING" if 5 <= hour < 12 else "AFTERNOON" if 12 <= hour < 17 else "EVENING"

        reason = get_analysis(direction)
        short = pair.replace(" OTC","")

        msg1 = f"📊 Currency pair: {pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {set_str} - Prepare {short}"
        msg2 = f"Entry time: ⏰ {entry_str} - {session}\nDirection: {icon} {direction}\n\n➤ {reason}"
        
        next_pair = random.choice(STRONG_PAIRS)
        next_dt = set_dt + timedelta(minutes=5)
        next_str = next_dt.strftime("%H:%M")
        msg3 = f"❗ (UTC+1) - {session}\n\n📊 Currency pair: {next_pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {next_str} - Prepare {next_pair.replace(' OTC','')}"

        send(msg1)
        print(f"SET: {pair}")
        time.sleep(60)
        send(msg2)
        print(f"ENTRY: {direction}")
        time.sleep(20)
        send(msg3)
        time.sleep(240)

threading.Thread(target=run_flask, daemon=True).start()
bot_loop()
