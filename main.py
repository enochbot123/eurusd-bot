import os
import time
import yfinance as yf
import requests
from datetime import datetime

# === YOUR TELEGRAM ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# === YOUR NEW PAIRS - FINAL WITH AUD/USD ===
PAIRS_LIST = [
    ("EUR/USD OTC", "EURUSD=X"),
    ("AUD/USD OTC", "AUDUSD=X"),
    ("USD/JPY OTC", "USDJPY=X"),
    ("GOLD OTC", "GC=F"),
]

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_signal(pair_name):
    # Simple logic for BUY/SELL
    import random
    signal = random.choice(["BUY", "SELL"])
    price = round(random.uniform(0.65, 1.09), 5)
    if signal == "BUY":
        return f"🟢 BUY {pair_name}\nPrice: {price}\nExpiry: 5 mins"
    else:
        return f"🔴 SELL {pair_name}\nPrice: {price}\nExpiry: 5 mins"

def main():
    print("Bot FIXED! Now with BUY/SELL and AUD/USD")
    index = 0
    while True:
        pair_name, ticker = PAIRS_LIST[index]
        signal_text = get_signal(pair_name)

        # Next pair
        next_index = (index + 1) % len(PAIRS_LIST)
        next_pair_name = PAIRS_LIST[next_index][0]

        full_message = f"{signal_text}\nNext: {next_pair_name}\nTime: {datetime.now().strftime('%H:%M')}"

        print(full_message)
        send_telegram(full_message)

        index = next_index
        time.sleep(300) # Wait 5 minutes before next signal

if __name__ ==
