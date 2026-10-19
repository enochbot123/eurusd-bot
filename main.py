import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = "8529194860"
CHANNEL_ID = "-1003714315133"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch System LIVE - Pro Clock + Sticker Bot ONLINE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=15)
    except:
        pass

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD"]

def bot_loop():
    time.sleep(5)
    last = ""
    send(MY_ID, "Bot LIVE - Clock + Sticker version")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            if h == 10 or h == 13 or h == 17:
                sess = "MORNING" if h==10 else "AFTERNOON" if h==13 else "EVENING"
            else:
                time.sleep(30)
                continue
            pair = random.choice(PAIRS)
            if pair == last:
                pair = random.choice(PAIRS)
            last = pair
            is_up = random.choice([True, False])
            direction = "UP" if is_up else "DOWN"
            dir_emoji = "\u2b06\ufe0f" if is_up else "\u2b07\ufe0f"
            sticker = "\U0001f4c8\U0001f7e9 UP \U0001f4c8" if is_up else "\U0001f4c9\U0001f7e5 DOWN \U0001f4c9"
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            short = pair.replace(" OTC","")
            # MESSAGE 1 - CLOCK
            m1 = "\u23f0 Currency pair: " + pair + "\n"
            m1 += "\u23f3 Expiration: 3 min [M3]\n"
            m1 += "\U0001f550 SET: " + set_str + " - Prepare " + short + " \U0001f3af\n"
            m1 += "\U0001f4b0 Payout: +92%"
            # MESSAGE 2 - ENTRY + DIRECTION STICKER
            m2 = "\U0001f680 Entry time: " + set_str + " - " + sess + "\n"
            if is_up:
                m2 += "\U0001f4c8 Direction: " + direction + " " + dir_emoji + "\n"
                m2 += "\U0001f7e9\U0001f7e9 BUY \U0001f7e9\U0001f7e9\n"
                m2 += "\U0001f525\U0001f4aa GO UP! \U0001f4aa\U0001f525"
            else:
                m2 += "\U0001f4c9 Direction: " + direction + " " + dir_emoji + "\n"
                m2 += "\U0001f7e5\U0001f7e5 SELL \U0001f7e5\U0001f7e5\n"
                m2 += "\U0001f525\U0001f4aa GO DOWN! \U0001f4aa\U0001f525"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(240)
        except Exception
