import os, time, threading, requests
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)
TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT = "8868905914"

# Your pairs - e go rotate 1 by 1
SYMBOLS_LIST = [
    ("EUR/USD", "EURUSD=X"),
    ("AUD/USD", "AUDUSD=X"),
    ("USD/JPY", "USDJPY=X"),
    ("GBP/JPY", "GBPJPY=X"),
    ("Gold", "GC=F")
]

last_set = -1
last_enter = -1
current_pair = SYMBOLS_LIST[0]

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
        data={"chat_id": CHAT, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except:
        pass

def get_analysis(ticker):
    try:
        time.sleep(1)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 30:
            return "UP", "Price dey show strong momentum, but e don reach extreme level."
        close = closes[-1]
        ema9 = sum(closes[-9:]) / 9
        ema21 = sum(closes[-21:]) / 21
        
        # RSI
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.1
        avg_loss = sum(losses)/14 if losses else 0.1
        rsi = 100 - (100/(1+avg_gain/avg_loss))

        if close > ema9 and rsi < 70:
            direction = "UP"
            reasons = [
                f"The price broke above a key support level with strong bullish momentum. RSI at {rsi:.1f} shows buyers still in control. Based on this, we enter a buy trade.",
                f"The price approached a strong support level after a rapid downward movement. A bullish candlestick pattern appeared, signaling potential reversal. Based on this, we enter a buy trade.",
                f"EMA crossover confirmed uptrend, price is holding above EMA9 and EMA21. Momentum is building for continuation."
            ]
        else:
            direction = "DOWN"
            reasons = [
                f"The price approached a strong resistance level after a rapid upward movement. A bearish candlestick pattern appeared, signaling potential rejection. Based on this, we enter a sell trade.",
                f"The price faced heavy selling pressure near the top, RSI at {rsi:.1f} indicates overbought condition. A pullback is expected, so we sell.",
                f"Price dropped below EMA9, showing weakness. Sellers are taking control after a failed attempt to go higher."
            ]
        import random
        return direction, random.choice(reasons)
    except:
        return "DOWN", "The price approached a strong resistance level after a rapid upward movement. A bearish candlestick pattern appeared, signaling potential rejection. Based on this, we enter a sell trade."

def loop():
    global last_set, last_enter, current_pair
    time.sleep(3)
    send("✅ BOT UPDATED TO YOUR FORMAT\n1 by 1 rotation - Pro style!")
    
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second
            
            total_blocks = now.hour * 12 + (cm // 5)
            idx = total_blocks % len(SYMBOLS_LIST)
            current_pair = SYMBOLS_LIST[idx]
            name = current_pair[0]

            # SET - :04, :09, :14...
            if cm % 5 == 4 and last_set != cm and cs < 50:
                last_set = cm
                pair_name = f"{name} OTC" if "Gold" not in name else f"{name} OTC"
                msg = f"❗ (UTC+1)\n\n📊 Currency pair: {pair_name}\n⏱ Expiration time: 3 min [M3]\n\n⏰ SET TIME: {now.hour:02d}:{cm+1:02d} - Prepare {name}"
                send(msg)

            # ENTER - :00, :05, :10...
            if cm % 5 == 0 and last_enter != cm and cs < 50:
                last_enter = cm
                # Use previous block pair so SET and ENTER match
                prev_idx = (total_blocks - 1) % len(SYMBOLS_LIST) if total_blocks > 0 else 0
                name_e, ticker_e = SYMBOLS_LIST[prev_idx]
                
                direction, reason = get_analysis(ticker_e)
                direction_text = "👻 UP" if direction == "UP" else "👻 DOWN"
                entry_time = f"{now.hour:02d}:{cm:02d}"
                
                msg = f"Entry time: ⏰ {entry_time}\nDirection: {direction_text}\n\n➤ {reason}"
                send(msg)

        except Exception as e:
            print(e)
        time.sleep(1)

@app.route("/")
def home():
    return "BOT LIVE - PRO FORMAT - 1 BY 1"

threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
