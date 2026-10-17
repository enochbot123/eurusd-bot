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

def get_price(ticker):
    try:
        time.sleep(1)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 20:
            return None, "BUY", 50
        close = closes[-1]
        ema9 = sum(closes[-9:]) / 9
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.1
        avg_loss = sum(losses)/14 if losses else 0.1
        rsi = 100 - (100/(1+avg_gain/avg_loss))
        direction = "BUY" if close > ema9 else "SELL"
        return close, direction, rsi
    except:
        return None, None, None

def loop():
    global last_set, last_enter
    time.sleep(3)
    send("✅ BOT BACK ONLINE - FIXED!")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second
            if cm % 5 == 4 and last_set != cm and cs < 50:
                last_set = cm
                lines = []
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_price(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "Gold" not in name and "JPY" not in name else f"{price:.2f}"
                    lines.append(f"{emoji} {direction} {name} | {pf} | RSI {rsi:.1f}")
                if lines:
                    send(f"⚠️ SET TIME NOW - 1 MIN LEFT!\n\n" + "\n".join(lines) + f"\n\n⏰ {now.strftime('%H:%M')} WAT\n📌 Prepare only!")
            if cm % 5 == 0 and last_enter != cm and cs < 50:
                last_enter = cm
                lines = []
                for name, ticker in SYMBOLS.items():
                    price, direction, rsi = get_price(ticker)
                    if price is None: continue
                    emoji = "🟢" if direction == "BUY" else "🔴"
                    pf = f"{price:.5f}" if "Gold" not in name and "JPY" not in name else f"{price:.2f}"
                    lines.append(f"{emoji} {direction} {name} | {pf} | RSI {rsi:.1f}")
                if lines:
                    send(f"🚀 ENTER NOW - 3 MINUTES!\n\n" + "\n".join(lines) + f"\n\n⏰ {now.strftime('%H:%M')} WAT\n📌 Click now!")
        except Exception as e:
            print(e)
        time.sleep(2)

@app.route("/")
def home():
    return "BOT LIVE"

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
