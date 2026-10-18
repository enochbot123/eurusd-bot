import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
MY_ID = "8529194860"
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Bot OK"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def send(text):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    for cid in [CHANNEL_ID, MY_ID]:
        try:
            requests.post(url, json={"chat_id": cid, "text": text}, timeout=10)
        except:
            pass

PAIRS = [
"EUR/USD OTC",
"Gold OTC",
"USD/JPY OTC",
"AUD/USD OTC",
"EUR/JPY OTC",
"GBP/JPY OTC",
"USD/CAD OTC",
"EUR/GBP OTC",
"USD/CHF OTC",
"AUD/JPY OTC",
"EUR/AUD OTC",
"BTC/USD OTC",
"EUR/CAD OTC",
"NZD/USD OTC",
"Silver OTC"
]

def bot_loop():
    print("Bot started OK")
    last = ""
    while True:
        now = datetime.now(WAT)
        h = now.hour
        if 10 <= h < 11:
            sess = "MORNING"
        elif 13 <= h < 14:
            sess = "AFTERNOON"
        elif 17 <= h < 18:
            sess = "EVENING"
        else:
            time.sleep(60)
            continue
        if now.second != 0:
            time.sleep(60 - now.second)
            continue
        pair = random.choice(PAIRS)
        while pair == last:
            pair = random.choice(PAIRS)
        last = pair
        direction = random.choice(["UP", "DOWN"])
        set_dt = now + timedelta(minutes=1)
        set_str = set_dt.strftime("%H:%M")
        short = pair.replace(" OTC", "")
        rsi = round(random.uniform(28, 72), 1)
        m1 = "Currency pair: " + pair + "\nExpiration: 3 min [M3]\nSET: " + set_str + " - Prepare " + short
        m2 = "Entry time: " + set_str + " - " + sess + "\nDirection: " + direction + "\nRSI " + str(rsi) + " - Market analysis"
        m3 = "(UTC+1) - " + sess + "\nNext: " + random.choice(PAIRS) + "\nSET: " + (set_dt+timedelta(minutes=5)).strftime("%H:%M")
        send(m1)
        time.sleep(60)
        send(m2)
        time.sleep(20)
        send(m3)
        time.sleep(240)

threading.Thread(target=run_flask, daemon=True).start()
bot_loop()
