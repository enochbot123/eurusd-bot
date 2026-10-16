import os, time, requests, pytz, yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch 2-Step Bot LIVE!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

PAIRS_LIST = [
    ("EUR/USD", "EURUSD=X"),
    ("GBP/USD", "GBPUSD=X"),
    ("USD/JPY", "USDJPY=X"),
    ("GOLD", "GC=F"),
    ("BTC/USD", "BTC-USD")
]

def send(msg):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=15)

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
    except: return None

def loop():
    send("✅ <b>2-Step Mode ON!</b>\n1 min warning + Enter Now!")
    idx = 0
    while True:
        try:
            tz = pytz.timezone("Africa/Lagos")
            name, sym = PAIRS_LIST[idx]
            res = analyze(sym)
            if not res:
                idx = (idx + 1) % len(PAIRS_LIST)
                time.sleep(300)
                continue

            # STEP 1: 1 MINUTE BEFORE - WARNING
            action = "🟢 BUY" if res["signal"]=="BUY" else "🔴 SELL" if res["signal"]=="SELL" else "🟡 WAIT"
            now = datetime.now(tz)
            enter_time = now + timedelta(minutes=1)

            msg1 = f"""⚠️ <b>SET TIME NOW - 1 MIN LEFT!</b>

💱 <b>Pair:</b> {name}
📊 <b>Signal:</b> {action}
💰 Price: {res['price']:.2f}

⏰ <b>Prepare your chart!</b>
Set to <b>5 MIN timeframe</b>
Entry in 1 minute: <b>{enter_time.strftime('%H:%M:%S')}</b>

Get ready..."""
            send(msg1)

            time.sleep(60) # wait 1 minute as you talk

            # STEP 2: ENTER NOW
            expiry = datetime.now(tz) + timedelta(minutes=5)
            msg2 = f"""🚀 <b>ENTER NOW!!!</b> 🚀

{action} <b>{name}</b>
💰 Price: {res['price']:.2f}

⏰ <b>TIME TO ENTER:</b> {datetime.now(tz).strftime('%H:%M:%S')} NOW!
⏳ <b>Expiry:</b> {expiry.strftime('%H:%M:%S')} (5 MIN)

🔗 Trade: {LINK}

Next: {PAIRS_LIST[(idx+1)%len(PAIRS_LIST)][0]}"""
            send(msg2)

            idx = (idx + 1) % len(PAIRS_LIST)
            time.sleep(240) # 4 mins + 1 min = 5 mins cycle
        except Exception as e:
            print(e)
            time.sleep(30)

loop()
