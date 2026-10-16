import os
import time
import random
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PAIRS = ["EUR/USD OTC", "AUD/USD OTC", "USD/JPY OTC", "GOLD OTC"]

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

i = 0
print("Bot FIXED with AUD/USD - Started!")
while True:
    pair = PAIRS[i]
    action = random.choice(["BUY", "SELL"])
    emoji = "🟢" if action == "BUY" else "🔴"
    next_pair = PAIRS[(i+1) % len(PAIRS)]

    msg = f"{emoji} {action} {pair}\nExpiry: 5 mins\nNext: {next_pair}\nTime: {datetime.now().strftime('%H:%M')}"
    print(msg)
    send(msg)
    i = (i+1) % len(PAIRS)
    time.sleep(300)
