import os
import time
import threading
import requests
import yfinance as yf
import pandas as pd
from flask import Flask
from datetime import datetime
import pytz
import numpy as np

app = Flask(__name__)

TELEGRAM_TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT_ID = "8868905914"

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X", 
    "USD/JPY": "USDJPY=X",
    "Gold": "XAUUSD=X"
}

# To avoid repeating same signal
last_signal = {}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=15)
        print(f"Sent {r.status_code}: {message[:40]}")
        return r.status_code == 200
    except Exception as e:
        print(f"Send error: {e}")
        return False

def get_rsi(data, period=14):
    try:
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    except:
        return 55.0

def get_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) < 20:
            return None, None, None
        close = float(df['Close'].iloc[-1])
        rsi = get_rsi(df)
        return close, rsi, df
    except Exception as e:
        print(f"Data error {ticker}: {e}")
        return None, None, None

def format_price(name, price):
    if "JPY" in name or "Gold" in name:
        return f"{price:.2f}"
    else:
        return f"{price:.5f}"

def check_markets():
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    minute = now.minute
    second = now.second
    
    # ONLY send signal at 2 times: :59 for SET TIME, :00 for ENTER
    # This stops spam!
    if minute == 59 and 0 <= second <= 20:
        phase = "SET"
    elif minute == 0 and 0 <= second <= 20:
        phase = "ENTER"
    else:
        return  # Do nothing other minutes = NO SPAM

    print(f"Checking phase {phase} at {now.strftime('%H:%M:%S')}")

    if 7 <= now.hour < 9:
        print("Paused 7-9AM")
        return

    for name, ticker in SYMBOLS.items():
        # Prevent same pair repeating within 5 mins
        key = f"{name}_{phase}_{now.hour}_{minute}"
        if key in last_signal:
            continue
        if f"{name}_{now.hour}" in last_signal and phase == "SET":
            # Already sent this hour
            if (datetime.now() - last_signal[f"{name}_{now.hour}"]).seconds < 300:
                continue

        price, rsi, _ = get_data(ticker)
        if price is None:
            continue
        
        # Filter: Only strong signals - avoids spam
        if rsi > 58:
            signal = "BUY"
            emoji = "🟢"
        elif rsi < 42:
            signal = "SELL"
            emoji = "🔴"
        else:
            continue  # Skip weak market = less spam

        price_fmt = format_price(name, price)
        rsi_fmt = f"{rsi:.1f}"

        if phase == "SET":
            msg = f"⚠️ SET TIME NOW 1 MIN LEFT!\n\n{emoji} {signal} {name} OTC Price {price_fmt} RSI {rsi_fmt} REAL 3 MIN"
            send_telegram(msg)
            last_signal[f"{name}_{now.hour}"] = datetime.now()
            last_signal[key] = True
        else: # ENTER
            msg = f"🚀 ENTER NOW!!!\n{emoji} {signal} {name} OTC Price {price_fmt} RSI {rsi_fmt} REAL 3 MIN"
            send_telegram(msg)
            last_signal[key] = True
        
        time.sleep(2)

def bot_loop():
    print("Bot started - OTC PRO mode - No Spam")
    send_telegram("✅ Enoch Bot Upgraded! Now na REAL OTC mode:\n⚠️ SET TIME 1 MIN LEFT\n🚀 ENTER NOW\n3 MIN expiry - No more spam every minute!")
    while True:
        try:
            check_markets()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(15) # Check every 15 sec for :59 and :00

@app.route("/")
def home():
    return "Bot LIVE - OTC Pro Mode - No Spam"

@app.route("/test")
def test():
    send_telegram("✅ TEST - New OTC format:\n⚠️ SET TIME NOW 1 MIN LEFT!\n🟢 BUY EUR/USD OTC Price 1.12435 RSI 60.9 REAL 3 MIN")
    time.sleep(2)
    send_telegram("🚀 ENTER NOW!!!\n🟢 BUY EUR/USD OTC Price 1.12435 RSI 60.9 REAL 3 MIN")
    return "Test sent in OTC format!"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
