import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X", 
    "USD/JPY": "USDJPY=X",
    "Gold": "GC=F",
    "EUR/USD OTC": "EURUSD=X"
}

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram Sent: {r.status_code}")
        if r.status_code != 200:
            print(r.text)
    except Exception as e:
        print(f"Send error: {e}")

def get_price(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=False)
        if df.empty or len(df) < 2:
            return None
        
        # FIXED HERE - This fixes your error "float() Series"
        close_price = float(df['Close'].iloc[-1])
        open_price = float(df['Open'].iloc[-1])
        
        return close_price, open_price
    except Exception as e:
        print(f"Check error {ticker}: {e}")
        return None

def check_markets():
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    print(f"Checking market at {now}")

    # Pause 7AM - 9AM Lagos time
    if 7 <= now.hour < 9:
        print("Market Paused Lagos 7-9AM")
        return

    for name, ticker in SYMBOLS.items():
        result = get_price(ticker)
        if result is None:
            continue
        
        close_p, open_p = result
        
        if close_p > open_p:
            signal = "🟢 BUY"
        else:
            signal = "🔴 SELL"
            
        message = f"""🚀 ENTER NOW!!! - {name}
{signal} - {name}
Price: {close_p:.5f}
Time: {now.strftime('%Y-%m-%d %H:%M:%S')} Lagos
"""
        send_telegram(message)
        time.sleep(3)

def bot_loop():
    print("Bot loop started...")
    while True:
        try:
            check_markets()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60)

@app.route("/")
def home():
    return "Bot is LIVE! Enoch's Bot is running."

@app.route("/test")
def test():
    send_telegram("✅ TEST SUCCESSFUL! Enoch, your bot is now WORKING! Error don fix!")
    return "Test sent! Check Telegram @Enoch_proket_bot"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
