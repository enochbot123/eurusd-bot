import os, time, requests, pytz, yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Bot WITH TIME LIVE!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "GOLD": "GC=F",
    "BTC/USD": "BTC-USD",
    "EUR/USD OTC": "EURUSD=X"
}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": False}, timeout=15)
    except Exception as e:
        print(e)

def analyze(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="1m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 30:
            return None
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
        if ema9 > ema21 and rsi_val > 50:
            return {"signal":"BUY", "price":price, "rsi":rsi_val}
        elif ema9 < ema21 and rsi_val < 50:
            return {"signal":"SELL", "price":price, "rsi":rsi_val}
        else:
            return {"signal":"WAIT", "price":price, "rsi":rsi_val}
    except:
        return None

def loop():
    send("✅ <b>BOT UPGRADED WITH TIME!</b>\nNow showing Entry & Expiry Time!")
    while True:
        try:
            tz = pytz.timezone("Africa/Lagos")
            now = datetime.now(tz)
            entry_time = now + timedelta(minutes=1)
            expiry_time = entry_time + timedelta(minutes=5)
            
            for name, sym in PAIRS.items():
                res = analyze(sym)
                if not res: continue
                if res["signal"] in ["BUY","SELL"]:
                    emoji = "🟢" if res["signal"]=="BUY" else "🔴"
                    msg = f"""{emoji} <b>{res['signal']} {name}</b> {emoji}

💰 Price: <code>{res['price']:.5f}</code>
📊 RSI: {res['rsi']:.1f}

⏰ <b>TIME TO ENTER:</b> {entry_time.strftime('%H:%M:%S')} Lagos
⏳ <b>EXPIRY:</b> {expiry_time.strftime('%H:%M:%S')} (5 MIN)
📅 Date: {now.strftime('%d %b %Y')}

🎯 Confidence: HIGH
🔗 Trade Now: {LINK}

<i>Next signal in 1 min</i>"""
                    send(msg)
                time.sleep(1)
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(30)

loop()
