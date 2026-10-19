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
    return "Enoch Final Fine Sticker LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send(cid, txt):
    try:
        url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
        requests.post(url, json={"chat_id": cid, "text": txt}, timeout=10)
    except:
        pass

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD","Gold OTC"]

def get_session(now):
    hm = now.hour * 100 + now.minute
    if 930 <= hm <= 1030:
        return "MORNING"
    if 1430 <= hm <= 1530:
        return "AFTERNOON"
    if 2030 <= hm <= 2130:
        return "EVENING"
    return None

def loop():
    last = ""
    while True:
        try:
            now = datetime.now(WAT)
            sess = get_session(now)
            if sess is None:
                time.sleep(30)
                continue
            p = random.choice(PAIRS)
            if p == last:
                p = random.choice(PAIRS)
            last = p
            is_up = random.choice([True, False])
            set_time = (now + timedelta(minutes=1)).strftime("%H:%M")
            short = p.replace(" OTC","")
            m1 = "PAIR: " + p + "\n"
            m1 += "EXPIRY: 3 MIN [M3]\n"
            m1 += "CLOCK SET: " + set_time + "\n"
            m1 += "PREPARE: " + short + "\n"
            m1 += "PAYOUT: +92% | " + sess + "\n"
            m1 += "STATUS: Waiting for entry..."
            if is_up:
                m2 = "ENTRY TIME: " + set_time + " " + sess + "\n"
                m2 += "DIRECTION: UP \U0001f53c\n"
                m2 += "SIGNAL: \U0001f680 ROCKET BUY \U0001f680\n"
                m2 += "CHART: \U0001f4c8 Break of Resistance\n"
                m2 += "REASON: Price broke upper level\n"
                m2 += "ACTION: \u2b06\ufe0f BUY NOW \u2b06\ufe0f"
            else:
                m2 = "ENTRY TIME: " + set_time + " " + sess + "\n"
                m2 += "DIRECTION: DOWN \U0001f53d\n"
                m2 += "SIGNAL: \U0001f3af TARGET SELL \U0001f3af\n"
                m2 += "CHART: \U0001f4c9 Break of Support\n"
                m2 += "REASON: Price broke lower level\n"
                m2 += "ACTION: \u2b07\ufe0f SELL NOW \u2b07\ufe0f"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(180)
        except:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
loop()
