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
    "Gold": "GC=F"
}

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Missing TOKEN/CHAT_ID")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=15)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Send error: {e}")

def get_price(ticker):
    try:
        # Download
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) == 0:
            return None

        # NEW FIX FOR YFINANCE - No more float(Series) error
        # Works even if yfinance returns Multi-index
        last_row = df.iloc[-1]
        
        # Get close price safely
        try:
            close_val = last_row['Close']
        except:
            close_val = last_row.iloc[3]  # fallback

        # If still Series, get first value
        if hasattr(close_val, 'iloc'):
            close_val = close_val.iloc[0]
        
        close_price = float(close_val)

        try:
            open_val = last_row['Open']
            if hasattr(open_val, 'iloc'):
                open_val = open_val.iloc[0]
            open_price = float(open_val)
        except:
            open_price = close_price

        return close_price, open_price

    except Exception as e:
        print(f"Check error {ticker}: {e}")
        return None

def check_markets():
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    print(f"Checking at {now.strftime('%H:%M:%S')} - {now}")

    # Pause 7-9 AM
    if 7 <= now.hour < 9:
        print("Paused 7-9AM Lagos")
        return

    for name, ticker in SYMBOLS.items():
        data = get_price(ticker)
        if data is None:
            continue
        
        close_p, open_p = data
        
        signal = "🟢 BUY" if close_p > open_p else "🔴 SELL"
            
        msg = f"🚀 ENTER NOW!!! - {name}\n{signal} {name}\nPrice: {close_p}\nTime: {now.strftime('%H:%M')} Lagos"
        send_telegram(msg)
        time.sleep(3)

def bot_loop():
    print("Bot started...")
    while True:
        try:
            check_markets()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60)

@app.route("/")
def home():
    return "Bot LIVE - Enoch fixed!"

@app.route("/test")
def test():
    send_telegram("✅ TEST SUCCESSFUL! Enoch, error don fix! Bot dey work now!")
    return "Test sent! Check Telegram"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
