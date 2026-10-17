import os, time, threading, requests
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)
TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT = "8868905914"

SYMBOLS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X", 
    "USD/JPY": "USDJPY=X",
    "Gold": "GC=F"
}

last_set = -1
last_enter = -1

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
        data={"chat_id": CHAT, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Send error: {e}")

def get_real_analysis(ticker):
    try:
        time.sleep(1.2) # To avoid Yahoo block
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        
        if len(closes) < 25:
            return None, None, None
            
        close = closes[-1]
        # EMA 9 and 21
        ema9 = sum(closes[-9:]) / 9
        ema21 = sum(closes[-21:]) / 21
        
        # RSI 14
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.01
        avg_loss = sum(losses)/14 if losses else 0.01
        rsi = 100 - (100/(1+avg_gain/avg_loss))

        # DIRECTION WITH EMA + RSI
        if close > ema9 and close > ema21 and rsi > 50:
            direction = "BUY"
        elif close < ema9 and close < ema21 and rsi < 50:
            direction = "SELL"
        else:
            direction = "BUY" if close > ema9 else "SELL"
            
        return close, direction, rsi
    except Exception as e:
        print(f"Error {ticker}: {e}")
        return None, None, None

def loop():
    global last_set, last_enter
    time.sleep(5)
    send("✅ BOT LIVE - FINAL MODE\n📊 Real Price + RSI + EMA\n📦 1 Message = All 4 Pairs\n⏰ Every 5 Mins | Honest Analysis")
    
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second

            # SET - 4 = :04, :09, :14, :19 etc - PREPARE ONLY
            if cm % 5 == 4 and last_set != cm and cs < 45:
                last_set = cm
                lines = []
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_real_analysis(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                    lines.append(f"{emoji} {direction} {name} OTC\n   💰 {pf} | RSI {rsi:.1f}")
                
                if lines:
                    msg = f"⚠️ SET TIME NOW - 1 MIN LEFT!\n━━━━━━━━━━━━━━\n" + "\n\n".join(lines) + f"\n━━━━━━━━━━━━━━\n⏰ {now.strftime('%H:%M')} WAT\n📌 Analysis only - Prepare, don't click yet!"
                    send(msg)

            # ENTER - 0 = :00, :05, :10, :15 etc - CLICK NOW
            if cm % 5 == 0 and last_enter != cm and cs < 45:
                last_enter = cm
                lines = []
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_real_analysis(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                    lines.append(f"{emoji} {direction} {name} OTC\n   💰 {pf} | RSI {rsi:.1f}")

                if lines:
                    msg = f"🚀 ENTER NOW - 3 MINUTES!\n━━━━━━━━━━━━━━\n" + "\n\n".join(lines) + f"\n━━━━━━━━━━━━━━\n⏰ {now.strftime('%H:%M')} WAT\n📌 Click now - 3 mins expiry - Manage risk!"
                    send(msg)

        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(1)

@app.route("/")
def home():
    return "BOT LIVE - FINAL MODE - 1 MESSAGE - REAL ANALYSIS"

@app.route("/test")
def test():
    lines = []
    for name, ticker in SYMBOLS.items():
        price, direction, rsi = get_real
