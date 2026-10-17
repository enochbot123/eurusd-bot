import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

# ===== YOUR REAL DETAILS - FIXED INSIDE =====
TELEGRAM_TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT_ID = "8868905914"
# =============================================

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "USDJPY=X",
    "Gold": "GC=F"
}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=data, timeout=15)
        print(f"Telegram status: {r.status_code}")
        if r.status_code != 200:
            print(f"Telegram error body: {r.text}")
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
    print(f"Checking at {now.strftime('%H:%M:%S')} Lagos")

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
    print("Bot started - Enoch final fixed version")
    send_telegram("✅ Bot don start! Enoch Proket Bot LIVE now! Bug fixed + Token fixed!")
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
    ok = send_telegram("✅ TEST SUCCESSFUL! Enoch your bot dey work! 200 OK! No more 404!")
    if ok:
        return "Test sent! Check Telegram @Enoch_proket_bot - 200 OK"
    else:
        return "Failed! Check logs"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
