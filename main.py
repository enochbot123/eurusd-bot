import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

# ===== PUT YOUR NEW TOKEN AND ID HERE DIRECTLY =====
TELEGRAM_TOKEN = "8529194860:AAF4jl6EbqTtBMyU6l77KtPayQjaAs-Gv3A"  # e.g. 8234567890:AAH...
CHAT_ID = "8868905914"   # your own ID - don change am if na still same
# =====================================================

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "USDJPY=X",
    "Gold": "GC=F"
}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/8529194860:AAEQqKUGwNqowpSyhyTJBhMY8qBkimpJHLk"
        data = {"chat_id": CHAT_ID, "8868905914": message}
        r = requests.post(url, data=data, timeout=15)
        print(f"Telegram status: {r.status_code} - {message[:40]}")
        return r.status_code == 200
    except Exception as e:
        print(f"Send error: {e}")
        return False

def get_price(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) == 0:
            return None
        last_row = df.iloc[-1]
        close_val = last_row['Close']
        if hasattr(close_val, 'iloc'):
            close_val = close_val.iloc[0]
        open_val = last_row['Open']
        if hasattr(open_val, 'iloc'):
            open_val = open_val.iloc[0]
        
        return float(close_val), float(open_val)
    except Exception as e:
        print(f"Check error {ticker}: {e}")
        return None

def check_markets():
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)
    print(f"Checking at {now.strftime('%H:%M:%S')}")

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
    print("Bot started - Enoch fixed version")
    # Send startup message
    send_telegram("✅ Bot don start! Enoch Proket Bot LIVE now!")
    while True:
        try:
            check_markets()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60)

@app.route("/")
def home():
    return "Bot LIVE - Enoch's Bot with Token inside!"

@app.route("/test")
def test():
    ok = send_telegram("✅ TEST SUCCESSFUL! Enoch, your bot dey work now! Token inside code work!")
    if ok:
        return "Test sent! Check Telegram"
    else:
        return "Failed! Check Token"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
