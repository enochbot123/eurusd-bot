import os, time, requests, yfinance as yf, pandas as pd, pytz
from datetime import datetime
from flask import Flask
import threading

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Bot V7 Live!"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
WAT = pytz.timezone("Africa/Lagos")

SYMBOLS = {"GOLD":"GC=F", "EUR/USD":"EURUSD=X", "AUD/USD":"AUDUSD=X", "USD/JPY":"JPY=X"}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def is_bad():
    h = datetime.now(WAT).hour
    return h==7 or h==8

def check(symbol, ticker):
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if len(df)<50: return
        close = df['Close']
        # RSI 14
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = -delta.where(delta<0,0).rolling(14).mean()
        rs = gain/loss
        rsi = 100 - (100/(1+rs))
        r = float(rsi.iloc[-1])

        # Alligator simplified
        jaw = close.rolling(13).mean().iloc[-1]
        teeth = close.rolling(8).mean().iloc[-1]
        lips = close.rolling(5).mean().iloc[-1]
        price = float(close.iloc[-1])

        if price>jaw and price>teeth and price>lips and r>50 and r<70:
            send(f"🚀 *ENTER NOW!!!* {symbol} 🟢 BUY\nPrice: {price:.2f}\nRSI: {r:.1f}\n⏰ {datetime.now(WAT).strftime('%I:%M %p')}\nSet 3 MIN!")
        elif price<jaw and price<teeth and price<lips and r<50 and r>30:
            send(f"🔻 *ENTER NOW!!!* {symbol} 🔴 SELL\nPrice: {price:.2f}\nRSI: {r:.1f}\n⏰ {datetime.now(WAT).strftime('%I:%M %p')}\nSet 3 MIN!")
    except Exception as e:
        print(e)

def bot_loop():
    print("V7 Started")
    paused=False
    while True:
        try:
            if is_bad():
                if not paused:
                    send("⏸️ *PAUSED* Lagos 7-9AM bad market - No signals till 9AM to protect you! 💤")
                    paused=True
                time.sleep(60)
                continue
            paused=False
            for name,tick in SYMBOLS.items():
                check(name,tick)
                time.sleep(2)
            time.sleep(30)
        except Exception as e:
            print(e)
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
