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
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT, "text": msg}, timeout=10)
    except:
        pass

def get_real_analysis(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 30:
            return None, "BUY", 50
        
        close = closes[-1]
        # EMA 9 & 21
        ema9 = sum(closes[-9:]) / 9
        ema21 = sum(closes[-21:]) / 21
        # Simple RSI 14
        gains = []
        losses = []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.1
        avg_loss = sum(losses)/14 if losses else 0.1
        rs = avg_gain / avg_loss
        rsi = 100 - (100/(1+rs))

        # REAL LOGIC
        if close > ema9 and close > ema21 and rsi > 50:
            direction = "BUY"
        elif close < ema9 and close < ema21 and rsi < 50:
            direction = "SELL"
        else:
            direction = "BUY" if close > ema9 else "SELL"
            
        return close, direction, rsi
    except Exception as e:
        print(f"Error {e}")
        return None, "BUY", 55

def loop():
    global last_set, last_enter
    time.sleep(3)
    send("✅ BOT LIVE - REAL MARKET ANALYSIS\nEvery 5 mins | Real Price + RSI + EMA\nNote: Analysis only, not 100% guarantee. Trade wisely!")
    
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second

            if cm % 5 == 4 and last_set != cm and cs < 50:
                last_set = cm
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_real_analysis(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                    msg = f"⚠️ SET TIME NOW - 1 MIN LEFT!\n\n{emoji} {direction} {name} OTC\n💰 Price: {pf}\n📊 RSI: {rsi:.1f} | EMA Trend\n⏰ {now.strftime('%H:%M')} WAT\n\n📌 Analysis only - Manage risk!"
                    send(msg)
                    time.sleep(1)

            if cm % 5 == 0 and last_enter != cm and cs < 50:
                last_enter = cm
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_real_analysis(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "JPY" not in name and "Gold" not in name else f"{price:.2f}"
                    msg = f"🚀 ENTER NOW - 3 MINUTES!\n\n{emoji} {direction} {name} OTC\n💰 Price: {pf}\n📊 RSI: {rsi:.1f} | EMA Trend\n⏰ {now.strftime('%H:%M')} WAT\n\n📌 Analysis only - Manage risk!"
                    send(msg)
                    time.sleep(1)
        except Exception as e:
            print(e)
        time.sleep(2)

@app.route("/")
def home():
    return "BOT LIVE - REAL ANALYSIS EVERY 5 MINS"
@app.route("/test")
def test():
    for name, ticker in SYMBOLS.items():
        price, direction, rsi = get_real_analysis(ticker)
        pf = f"{price:.5f}" if price else "0"
        send(f"🧪 TEST REAL ANALYSIS\n{direction} {name} {pf} RSI {rsi:.1f}")
        time.sleep(0.5)
    return "Test sent!"

threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
