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
    return "Enoch Bot LIVE - 10:52 AM Fixed"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=data, timeout=15)
    except Exception as e:
        print(e)

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD"]

def bot_loop():
    time.sleep(5)
    last = ""
    print("Bot started")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            if h == 10 or h == 13
