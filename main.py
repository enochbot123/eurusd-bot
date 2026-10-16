import os, time, requests, pytz, yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch PREPARE & ENTER Bot LIVE!"
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
    send("✅ <b>Bot Updated - Prepare + Enter Mode!</b>\nNow e go first tell you to SET TIME!")
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

            now = datetime.now(tz)
            prepare_entry = now + timedelta(minutes=1)
            expiry = prepare_entry + timedelta(minutes=5)

            # STEP 1 - PREPARE MESSAGE (As you talk am)
            if res["signal"] == "BUY": action = "🟢 BUY"
            elif res["signal"] == "SELL": action = "🔴 SELL"
            else: action = "🟡 WAIT"

            prepare_msg = f"""⚠️ <b>GET READY!</b>

👉 <b>SET YOUR TIME NOW!</b>
Set your chart to <b>5 MIN timeframe</b>

💱 <b>Pair wey you go trade:</b> {name}
📊 Signal: {action}
💰 Price: {res['price']:.2f}

⏰ <b>TIME WEY YOU GO ENTER:</b>
<b>{prepare_entry.strftime('%H:%M:%S')} Lagos</b>
(You get 1 minute to prepare)

⏳ Expiry: {expiry.strftime('%H:%M:%S')} (5 MIN)

Prepare now..."""
            send(prepare_msg)
            print(f"Prepare sent for {name}")

            # Wait 1 minute to give them time to set
            time.sleep(60)

            # STEP 2 - ENTER NOW MESSAGE
            enter_msg = f"""🚀 <b>ENTER NOW! ENTER NOW!</b> 🚀

{action} <b>{name}</b>

💰 Enter Price: {res['price']:.2f}
📊 RSI: {res['rsi']:.1f}

⏰ <b>TIME TO ENTER:</b> {datetime.now(tz).strftime('%H:%M:%S')} NOW!!!
⏳ <b>EXPIRY:</b> {(datetime.now(tz)+timedelta(minutes=5)).strftime('%H:%M:%S')} (5 MIN)

🔗 Trade Here: {LINK}

Next pair: {PAIRS_LIST[(idx+1)%len(PAIRS_LIST)][0]} in 4 mins"""
            send(enter_msg)
            print(f"Enter sent for {name}")

            idx = (idx + 1) % len(PAIRS_LIST)
            time.sleep(240) # 4 mins + 1 min before = 5 mins total per pair
        except Exception as e:
            print(e)
            time.sleep(30)

loop()
