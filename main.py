import os
import time
import requests
import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Enoch Bot V7 Live - With 7AM Pause!"

@app.route('/test')
def test():
    send("TEST - Telegram dey work! Bot V7 Live!")
    return "Test sent! Check Telegram!"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WAT = pytz.timezone("Africa/Lagos")

SYMBOLS = {
    "GOLD": "GC=F",
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "JPY=X"
}

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=10)
        print(f"Sent: {msg}")
    except Exception as e:
        print(f"Send error: {e}")

def is_bad_hour():
    hour = datetime.now(WAT).hour
    return hour == 7 or hour == 8

def check_signal(name, ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if len(df) < 50:
            return
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        r = float(rsi.iloc[-1])
        jaw = float(close.rolling(13).mean().iloc[-1])
        teeth = float(close.rolling(8).mean().iloc[-1])
        lips = float(close.rolling(5).mean().iloc[-1])
        price = float(close.iloc[-1])
        time_now = datetime.now(WAT).strftime('%I:%M %p')
        if price > jaw and price > teeth and price > lips and r > 50 and r < 70:
            send(f"ENTER NOW!!! {name} BUY Price: {price:.2f} RSI: {r:.1f} Time: {time_now} Set 3 MIN!")
        elif price < jaw and price < teeth and price < lips and r < 50 and r > 30:
            send(f"ENTER NOW!!! {name} SELL Price: {price:.2f} RSI: {r:.1f} Time: {time_now} Set 3 MIN!")
    except Exception as e:
        print(f"Check error {name}: {e}")

def bot_loop():
    print("Enoch Bot V7 Started!")
    paused_sent = False
    while True:
        try:
            if is_bad_hour():
                if not paused_sent:
                    send("MARKET PAUSED - Lagos 7AM-9AM na bad market! Bot dey sleep till 9AM!")
                    paused_sent = True
                time.sleep(60)
                continue
            paused_sent = False
            for name, ticker in SYMBOLS.items():
                check_signal(name, ticker)
                time.sleep(2)
            time.sleep(30)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
