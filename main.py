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
    except Exception as e:
        print(e)

def get_signal():
    try:
        data = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
        if len(data) < 50:
            return None
        close = data['Close']
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        last = float(close.iloc[-1])
        if ema9 > ema21 and last > ema9:
            return "UP", last
        elif ema9 < ema21 and last < ema9:
            return "DOWN", last
        else:
            return None
    except:
        return None

while True:
    now_wat = datetime.now(WAT)
    print(f"Checking... {now_wat}")
    result = get_signal()
    
    if result:
        direction, price = result
        entry_dt = now_wat + timedelta(minutes=2)
        entry_str = entry_dt.strftime("%I:%M %p")
        
        icon = "🟢" if direction == "UP" else "🔴"
        
        msg1 = "🚀 <b>ENOCH STRATEGY - REAL SIGNAL</b> 🚀\n\n" + f"Pair: <b>EUR/USD</b>\nEntry Time: <b>{entry_str} WAT</b>\nPrice: {price:.5f}\n\nGet ready... Direction dey come in 1 min"
        send(msg1)
        
        time.sleep(60)
        
        msg2 = "✅ <b>DIRECTION CONFIRMED</b> ✅\n\n" + f"EUR/USD\nEntry: {entry_str} WAT\nDirection: <b>{direction} {icon}</b>\n\nExpiry: 1 Minute\nRisk 1% only!"
        send(msg2)
        
        time.sleep(600)
    else:
        time.sleep(120)
