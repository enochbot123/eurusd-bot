import os
import time
import threading
import requests
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

TELEGRAM_TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT_ID = "8868905914"

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X", 
    "USD/JPY": "USDJPY=X",
    "Gold": "XAUUSD=X"
}

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)
        print(f"SENT: {message[:30]}")
    except Exception as e:
        print(e)

def get_data(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=True)
        if df.empty or len(df) < 20:
            return None, None, None
        close = float(df['Close'].iloc[-1])
        open_p = float(df['Open'].iloc[-1])
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain/loss))
        rsi_val = float(rsi.iloc[-1]) if not rsi.empty else 55.0
        direction = "BUY" if close > open_p else "SELL"
        return close, rsi_val, direction
    except:
        return None, None, None

def bot_loop():
    print("Bot started - EVERY 5 MINS MODE")
    send_telegram("✅ Bot UPDATED - Now e go send EVERY 5 MINUTES! No filter!")
    last_sent_minute = -1
    
    while True:
        try:
            lagos = pytz.timezone("Africa/Lagos")
            now = datetime.now(lagos)

            # EVERY 5 MINUTES: SET at :04, :09, :14, :19, :24, :29, :34, :39, :44, :49, :54, :59
            if now.minute % 5 == 4 and 0 <= now.second <= 20:
                if last_sent_minute != now.minute:
                    for name, ticker in SYMBOLS.items():
                        price, rsi, direction = get_data(ticker)
                        if price is None: continue
                        emoji = "🟢" if direction == "BUY" else "🔴"
                        price_f = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                        msg = f"⚠️ SET TIME NOW 1 MIN LEFT!\n\n{emoji} {direction} {name} OTC Price {price_f} RSI {rsi:.1f} REAL 3 MIN"
                        send_telegram(msg)
                        time.sleep(1)
                    last_sent_minute = now.minute

            # EVERY 5 MINUTES: ENTER at :00, :05, :10, :15, :20, :25, :30, :35, :40, :45, :50, :55
            if now.minute % 5 == 0 and 0 <= now.second <= 20:
                if last_sent_minute != now.minute:
                    for name, ticker in SYMBOLS.items():
                        price, rsi, direction = get_data(ticker)
                        if price is None: continue
                        emoji = "🟢" if direction == "BUY" else "🔴"
                        price_f = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                        msg = f"🚀 ENTER NOW!!!\n{emoji} {direction} {name} OTC Price {price_f} RSI {rsi:.1f} REAL 3 MIN"
                        send_telegram(msg)
                        time.sleep(1)
                    last_sent_minute = now.minute

        except Exception as e:
            print(f"Error: {e}")
        time.sleep(5)

@app.route("/")
def home():
    return "Bot LIVE - Every 5 Mins"

@app.route("/test")
def test():
    send_telegram("⚠️ SET TIME NOW 1 MIN LEFT!\n\n🟢 BUY EUR/USD OTC Price 1.12435 RSI 60.9 REAL 3 MIN")
    time.sleep(1)
    send_telegram("🚀 ENTER NOW!!!\n🟢 BUY EUR/USD OTC Price 1.12435 RSI 60.9 REAL 3 MIN")
    return "Test sent!"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
