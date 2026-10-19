import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return "OK LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send(cid, txt):
    try:
        url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
        requests.post(url, json={"chat_id": cid, "text": txt}, timeout=10)
    except:
        pass

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD"]

def loop():
    last = ""
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            if h == 10:
                s = "MORNING"
            elif h == 13:
                s = "AFTERNOON"
            elif h == 17:
                s = "EVENING"
            else:
                time.sleep(30)
                continue
            p = random.choice(PAIRS)
            if p == last:
                p = random.choice(PAIRS)
            last = p
            d = random.choice(["UP","DOWN"])
            set_time = (now + timedelta(minutes=1)).strftime("%H:%M")
            send(CHANNEL_ID, "Pair: " + p + " SET " + set_time + " 3min +92%")
            time.sleep(60)
            send(CHANNEL_ID, "Entry " + set_time + " " + s + " Dir " + d)
            time.sleep(240)
        except:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
loop()
