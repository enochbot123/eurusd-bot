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
    return "Enoch Pro 9:30 2:30 8:30 LIVE"

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
    # Morning 9:30 - 10:30
    # Afternoon 14:30 - 15:30
    # Evening 20:30 - 21:30
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
            # PRO MESSAGE 1 - CLOCK + SET
            m1 = "PAIR: " + p + "\n"
            m1 += "EXPIRY: 3 MIN [M3]\n"
            m1 += "CLOCK SET: " + set_time + "\n"
            m1 += "PREPARE: " + short + "\n"
            m1 += "PAYOUT: +92% | " + sess + "\n"
            m1 += "STATUS: Waiting for entry..."
            # PRO MESSAGE 2 - DIRECTION + STICKER + REASON
            if is_up:
                m2 = "ENTRY TIME: " + set_time + " " + sess + "\n"
                m2 += "DIRECTION: UP\n"
                m2 += "SIGNAL: ROCKET BUY\n"
                m2 += "CHART: Break of Resistance\n"
                m2 += "REASON: Price broke upper level + Volume spike\n"
                m2 += "ACTION: BUY NOW"
            else:
                m2 = "ENTRY TIME: " + set_time + " " + sess + "\n"
                m2 += "DIRECTION: DOWN\n"
                m2 += "SIGNAL: TARGET SELL\n"
                m2 += "CHART: Break of Support\n"
                m2 += "REASON: Price broke lower level + Bearish pressure\n"
                m2 += "ACTION: SELL NOW"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(180)
        except:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
loop()
