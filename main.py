import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = "8529194860"
CHANNEL_ID = "-1003714315133"
MY_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)

@app.route('/')
def home():
    return "Enoch System LIVE - 5 Pairs Pro +92% ONLINE"

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
    wm = False
    wa = False
    we = False
    send(MY_ID, "Bot LIVE - New 5 Pairs")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            m = now.minute
            if h == 9 and m == 45 and not wm:
                send(CHANNEL_ID, "MORNING REMINDER 9:45 AM - Morning Starts in 15 MINS 10AM-11AM UTC")
                wm = True
            if h == 9 and m == 55:
                send(CHANNEL_ID, "FINAL CALL MORNING IN 5 MINS 10AM Sharp")
            if h == 12 and m == 45 and not wa:
                send(CHANNEL_ID, "AFTERNOON REMINDER 12:45 PM - Starts in 15 MINS 1PM-2PM")
                wa = True
            if h == 12 and m == 55:
                send(CHANNEL_ID, "FINAL CALL AFTERNOON IN 5 MINS 1PM Sharp")
            if h == 16 and m == 45 and not we:
                send(CHANNEL_ID, "EVENING REMINDER 4:45 PM - Starts in 15 MINS 5PM-6PM")
                we = True
            if h == 16 and m == 55:
                send(CHANNEL_ID, "FINAL CALL EVENING IN 5 MINS 5PM Sharp")
            if h == 11:
                wm = False
            if h == 14:
                wa = False
            if h == 18:
                we = False
            if h == 10 or h == 13 or h == 17:
                sess = "MORNING" if h==10 else "AFTERNOON" if h==13 else "EVENING"
            else:
                if h==9 or h==12 or h==16:
                    time.sleep(30)
                    continue
                else:
                    time.sleep(60)
                    continue
            pair = random.choice(PAIRS)
            if pair == last:
                pair = random.choice(PAIRS)
            last = pair
            direction = random.choice(["UP","DOWN"])
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            m1 = "Currency pair: " + pair + " Expiration: 3 min [M3] SET: " + set_str + " Payout +92%"
            m2 = "Entry time: " + set_str + " " + sess + " Direction: " + direction
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(240)
        except Exception as e:
            print(e)
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
bot_loop()
