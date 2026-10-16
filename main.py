import os, time, requests, pytz, yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Rotation Bot LIVE!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

# This order e go follow - one by one
PAIRS_LIST = [
    ("EUR/USD", "EURUSD=X"),
    ("GBP/USD", "GBPUSD=X"),
    ("USD/JPY", "USDJPY=X"),
    ("GOLD", "GC=F"),
    ("BTC/USD", "BTC-USD")
]

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=20)
    except Exception as e:
        print(e)

def analyze(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="5m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 20: return None
        close = data['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = float(rsi.iloc[-1])
        price = float(close.iloc[-1])
        if ema9 > ema21 and rsi_val > 50: sig = "BUY"
        elif ema9 < ema21 and rsi_val < 50: sig = "SELL"
        else: sig = "WAIT"
        return {"signal":sig, "price":price, "rsi":rsi_val}
    except:
        return None

def loop():
    send("✅ <b>Rotation Mode ON!</b>\nOne pair every 5 mins\nWith ENTRY TIME!")
    idx = 0
    while True:
        try:
            tz = pytz.timezone("Africa/Lagos")
            now = datetime.now(tz)
            entry = now + timedelta(minutes=1)
            expiry = entry + timedelta(minutes=5)

            name, sym = PAIRS_LIST[idx]
            res = analyze(sym)

            if res:
                if res["signal"] == "BUY": title = "🟢 BUY"
                elif res["signal"] == "SELL": title = "🔴 SELL"
                else: title = "🟡 WAIT"

                msg = f"""{title} <b>{name}</b>

💰 Price: {res['price']:.2f}
📊 RSI: {res['rsi']:.1f}

⏰ <b>TIME TO ENTER:</b> {entry.strftime('%H:%M:%S')} Lagos
⏳ <b>EXPIRY:</b> {expiry.strftime('%H:%M:%S')} (5 MIN)
⏱️ Timeframe: 5 MIN

🔗 Trade Here: {LINK}

Next Pair: {PAIRS_LIST[(idx+1)%len(PAIRS_LIST)][0]} in 5 mins"""
                send(msg)
                print(f"Sent {name}")

            idx = (idx + 1) % len(PAIRS_LIST)
            time.sleep(300) # wait 5 mins before next single pair
        except Exception as e:
            print(e)
            time.sleep(30)

loop()
