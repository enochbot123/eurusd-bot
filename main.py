import os, time, random, requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Bot V3 LIVE - Running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_flask, daemon=True).start()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
POCKET_LINK = os.environ.get("POCKET_LINK") or "..."
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except: pass

def trading_loop():
    send_telegram("✅ <b>Enoch Bot V3 is LIVE and sending signals!</b>")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            signals = ["BUY EUR/USD - 1 MIN", "SELL EUR/USD - 1 MIN"]
            signal = random.choice(signals)
            msg = f"📊 <b>{signal}</b>\n⏰ {now.strftime('%H:%M:%S')} Lagos\n🔗 Trade: {POCKET_LINK}"
            send_telegram(msg)
            print(f"[{now}] Sent: {signal}")
            time.sleep(300)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

trading_loop()
            now = datetime.now(pytz.timezone("Africa/Lagos")).strftime("%H:%M:%S")
            # Example signal logic - you fit change am
            signals = ["BUY EUR/USD - 1 MIN", "SELL EUR/USD - 1 MIN", "WAIT"]
            signal = random.choice(signals)
            # send_telegram(f"📊 {now}\nSignal: {signal}\nLink: {POCKET_LINK}")
            print(f"[{now}] {signal}")
            time.sleep(300)  # 5 mins
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    trading_loop()
    
