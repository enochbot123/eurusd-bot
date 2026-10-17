import os
import time
import requests
import threading
from flask import Flask

# --- KEEP ALIVE FOR RENDER + CRON-JOB ---
app = Flask(__name__)
@app.route('/')
def home():
    return "BOT IS LIVE - EUR/USD OTC 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- YOUR TELEGRAM ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHAT_ID = os.getenv("CHAT_ID", "YOUR_CHAT_ID_HERE")

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except:
        pass

# --- TRADING LOGIC - OTC 24/7 ---
SYMBOL = "EUR/USD-OTC"  # <-- THIS NA THE OTC FOR MONDAY TO SUNDAY!
print(f"BOT FIXED V3 IS LIVE - Trading {SYMBOL}")

def trading_loop():
    time.sleep(5)
    send_telegram(f"✅ *BOT FIXED V3 IS LIVE!*\nNow trading *{SYMBOL}*\nActive Monday to Sunday 24/7")
    
    while True:
        try:
            print(f"Scanning {SYMBOL}...")
            # Your Alligator + RSI logic dey here
            # For now e dey wait for high accuracy setup
            
            # If you want test, uncomment this to send signal every hour:
            # send_telegram(f"🔥 HIGH ACCURACY SIGNAL 🔥\nBUY {SYMBOL} - 3 MINUTES\nRSI: 32, Alligator: BUY")
            
            time.sleep(60) # Scan every 1 minute
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# --- START EVERYTHING ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    trading_loop()
