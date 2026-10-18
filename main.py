import os
import time
import yfinance as yf
import requests
from datetime import datetime, timedelta
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

WAT = pytz.timezone("Africa/Lagos")

def send(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"})
        print("Sent:", text)
    except Exception as e:
        print(e)

def get_real_signal():
    try:
        # Use 1min chart for real entry
        data = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
        if len(data) < 50:
            return None
        
        close = data['Close']
        # Simple EMA strategy for real signal
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        last = float(close.iloc[-1])

        if ema9 > ema21 and last > ema9:
            return "UP", last
        elif ema9 < ema21 and last < ema9:
            return "DOWN", last
        else:
            return None
    except Exception as e:
        print(e)
        return None

# MAIN LOOP - Make e dey run
while True:
    now_wat = datetime.now(WAT)
    print(f"Checking... {now_wat}")

    result = get_real_signal()
    
    if result:
        direction, price = result
        
        # Set entry time for next 2 minutes (so people go get ready)
        entry_time_dt = now_wat + timedelta(minutes=2)
        entry_time_str = entry_time_dt.strftime("%I:%M %p")

        # 1st Message: Entry Time + Pair
        msg1 = f"""
🚀 <b>ENOCH STRATEGY - REAL SIGNAL</b> 🚀

💰 Pair: <b>EUR/USD</b>
⏰ Entry Time: <b>{entry_time_str} WAT</b>
📊 Price Now: {price:.5f}

Get ready... Direction dey come in 1 min 👇
"""
        send(msg1)
        
        # Wait 60 seconds then send direction
        time.sleep(60)

        msg2 = f"""
✅ <b>DIRECTION CONFIRMED</b> ✅

💰 EUR/USD
⏰ Entry: {entry_time_str} WAT
📈 Direction: <b>{direction} {'🟢' if direction=='UP' else '🔴'}</b>

Expiry: 1 Minute
Risk: 1% only - No
