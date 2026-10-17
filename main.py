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

# Pairs to check - same as your own
SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X", 
    "USD/JPY": "USDJPY=X",
    "Gold OTC": "GC=F",
    "EURUSD OTC": "EURUSD=X"
}

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Missing TOKEN or CHAT_ID")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=10)
        print(f"Sent: {message[:50]}... Status: {r.status_code}")
        if r.status_code != 200:
            print(f"Telegram error: {r.text}")
    except Exception as e:
        print(f"Send error: {e}")

def get_price(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if df.empty:
            return None, None, None, None
        
        # FIXED: Use iloc[-1] to avoid Series error
        # This was your bug - float(Series) -> now fixed
        close_price = float(df['Close'].iloc[-1])
        open_price = float(df['Open'].iloc[-1])
        high_price = float(df['High'].iloc[-1])
        low_price = float(df['Low'].iloc[-1])
        
        return close_price, open_price, high_price, low_price
    except Exception as e:
        print(f"Check error {ticker}: {e}")
        return None, None, None, None

def check_markets():
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    
    # Lagos 7AM-9AM Pause (as in your logs)
    if 7 <= now.hour < 9:
        msg = f"⏸️ MARKET PAUSED - Lagos {now.strftime('%I%p')}-{now.strftime('%I%p')} Low Volatility"
        # Only send once per hour to avoid spam
        if now.minute == 0:
            send_telegram(msg)
        print(f"Paused: {now}")
        return

    for name, ticker in SYMBOLS.items():
        close_p, open_p, high_p, low_p = get_price(ticker)
        if close_p is None:
            continue
        
        # Simple signal logic - you can change this to your own strategy
        if close_p > open_p:
            signal = "🟢 BUY"
        else:
            signal = "🔴 SELL"
            
        message = f"""🚀 ENTER NOW!!! - {name}
{signal} {name}
Price: {close_p}
Time: {now.strftime('%Y-%m-%d %H:%M:%S')} Lagos
"""
        send_telegram(message)
        time.sleep(2) # avoid Telegram flood

def bot_loop():
    print("Bot loop started...")
    while True:
        try:
            check_markets()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60) # check every 1 minute

@app.route("/")
def home():
    return "Bot is LIVE! Enoch's Bot is running. Go to /test to test Telegram."

@app.route("/test")
def test():
    send_telegram("✅ TEST SUCCESSFUL! Your bot @Enoch_proket_bot is now WORKING! Price fix don work! - Enoch")
    return "Test message sent! Check your Telegram @Enoch_proket_bot"

# Start bot in background
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
