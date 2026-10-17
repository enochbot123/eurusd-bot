import os
import time
import requests
import ccxt
import pandas as pd
import ta
from datetime import datetime
import pytz

# === CONFIG ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SYMBOLS = ["GOLD", "EUR/USD", "AUD/USD", "USD/JPY"]

WAT = pytz.timezone("Africa/Lagos")

def is_bad_hour():
    now_wat = datetime.now(WAT)
    hour = now_wat.hour
    # Pause 7AM, 8AM Lagos = 7,8 hour
    if hour in [7, 8]:
        return True, now_wat.strftime("%I:%M %p")
    return False, ""

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def check_signal(symbol):
    # Your Alligator + RSI logic here (same as V6)
    # ... keep your existing logic ...
    return True, "BUY", 28.5, 1050.50  # example

print("Enoch V7 Started - With Bad Hour Filter")

last_pause_msg = ""

while True:
    try:
        bad, time_str = is_bad_hour()
        
        if bad:
            if last_pause_msg != time_str.split(":")[0]: # send once per hour
                send_telegram(f"⏸️ *MARKET PAUSED* ⏸️\nBad Hour Detected: {time_str} Lagos\nNo signals till 9AM to save your balance! 💤")
                last_pause_msg = time_str.split(":")[0]
            time.sleep(60)
            continue
        
        last_pause_msg = ""
        
        for sym in SYMBOLS:
            # Your existing V6 scanning loop
            # if signal found:
            # send_telegram(f"🚀 ENTER NOW!!! {sym}...")
            
        time.sleep(10)
        
    except Exception as e:
        print(e)
        time.sleep(10)
