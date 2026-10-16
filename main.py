import os, time, requests, pytz, yfinance as yf
import pandas as pd
from datetime import datetime
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Multi-Pair Bot LIVE!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X", 
    "USD/JPY": "USDJPY=X",
    "GOLD": "GC=F",
    "BTC/USD": "BTC-USD"
}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=15)
        print(f"Sent: {msg[:50]}")
    except Exception as e:
        print(f"TG error: {e}")

def analyze(symbol):
    try:
        data = yf.download(symbol, period="2d", interval="5m", progress=False, auto_adjust=True)
        if data.empty or len(data) < 20:
            return {"signal":"ERROR", "price":0, "rsi":0, "conf":"No data"}
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
            sig = "BUY"
        elif ema9 < ema21 and rsi_val < 50:
            sig = "SELL"
        else:
            sig = "WAIT"
        conf = "HIGH" if (rsi_val < 35 or rsi_val > 65) else "MED"
        return {"signal":sig, "price":price, "rsi":rsi_val, "conf":conf}
    except Exception as e:
        print(f"Analyze error {symbol}: {e}")
        return {"signal":"ERROR", "price":0, "rsi":0, "conf":str(e)[:20]}

def loop():
    send("🚀 <b>Enoch Bot FIXED - Now Sending ALWAYS!</b>\n✅ 5 Pairs | Every 5 mins")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            lines = []
            for name, yf_symbol in PAIRS.items():
                res = analyze(yf_symbol)
                if res["signal"] == "BUY": emoji = "🟢 BUY"
                elif res["signal"] == "SELL": emoji = "🔴 SELL"
                elif res["signal"] == "WAIT": emoji = "🟡 WAIT"
                else: emoji = "⚠️ ERROR"
                lines.append(f"{emoji} {name}: {res['price']:.2f} | RSI {res['rsi']:.1f}")
                time.sleep(0.5)
            
            msg = f"📊 <b>MARKET SCAN - {now.strftime('%H:%M:%S')}</b>\n\n" + "\n".join(lines) + f"\n\n🔗 {LINK}\nNext in 5 mins"
            send(msg)
            time.sleep(300)
        except Exception as e:
            print(f"Loop error: {e}")
            send(f"⚠️ Bot error: {e}")
            time.sleep(60)

loop()
