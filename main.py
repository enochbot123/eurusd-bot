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

# ALL PAIRS - you fit add more here
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
    except Exception as e:
        print(f"TG error: {e}")

def analyze(symbol):
    try:
        data = yf.download(symbol, period="1d", interval="5m", progress=False)
        if len(data) < 25: return None
        close = data['Close']
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + gain/loss))
        rsi_val = float(rsi.iloc[-1])
        price = float(close.iloc[-1])
        
        if ema9 > ema21 and 45 < rsi_val < 68:
            return {"signal":"BUY", "price":price, "rsi":rsi_val, "conf":"HIGH" if rsi_val < 62 else "MED"}
        elif ema9 < ema21 and 32 < rsi_val < 55:
            return {"signal":"SELL", "price":price, "rsi":rsi_val, "conf":"HIGH" if rsi_val > 38 else "MED"}
        else:
            return {"signal":"WAIT", "price":price, "rsi":rsi_val, "conf":"LOW"}
    except:
        return None

def loop():
    send("🚀 <b>Enoch MULTI-PAIR Bot UPGRADED!</b>\n✅ Scanning 5 Markets\n📊 EUR/USD | GBP/USD | USD/JPY | GOLD | BTC\n⏰ Every 5 mins with REAL analysis")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            results = []
            for name, yf_symbol in PAIRS.items():
                res = analyze(yf_symbol)
                if res and res['signal'] != "WAIT":
                    emoji = "🟢" if res['signal']=="BUY" else "🔴"
                    results.append(f"{emoji} <b>{res['signal']} {name}</b>\n   💰 {res['price']:.2f} | RSI {res['rsi']:.1f} | {res['conf']}")
                time.sleep(1)
            
            if results:
                header = f"🔥 <b>TOP SIGNALS - {now.strftime('%H:%M')} Lagos</b>\n\n"
                footer = f"\n\n🔗 Trade: {LINK}\n⚡ Next scan in 5 mins"
                msg = header + "\n\n".join(results) + footer
                send(msg)
                print(f"Sent {len(results)} signals")
            else:
                print(f"[{now}] No clear setup - all WAIT")
                # Send WAIT update every 15 mins only to avoid spam
                if now.minute % 15 == 0:
                    send(f"⏸️ <b>Market Scanning...</b>\nNo high-confidence setup now. All pairs choppy.\n⏰ {now.strftime('%H:%M:%S')} Lagos")
            
            time.sleep(300)
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

loop()
