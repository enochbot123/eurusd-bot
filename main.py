# -*- coding: utf-8 -*-
import os, time, requests, threading, random, json
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
MY_ID = os.getenv("MY_ID", "8529194860")
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot LIVE with Stats"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# --- STATS FILE ---
STATS_FILE = "stats.json"
def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"MORNING":0, "AFTERNOON":0, "EVENING":0, "date": str(datetime.now(WAT).date())}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

stats = load_stats()

def send(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
    except Exception as e:
        print(e)

def send_to_all(text):
    for cid in [CHANNEL_ID, MY_ID]:
        send(cid, text)

def get_menu():
    today = stats.get("date")
    if today != str(datetime.now(WAT).date()):
        # new day, reset
        stats["MORNING"]=0
        stats["AFTERNOON"]=0
        stats["EVENING"]=0
        stats["date"]=str(datetime.now(WAT).date())
        save_stats(stats)

    return f"""
❗ <b>THIS IS NOT GAMBLING
THIS IS STRATEGY</b> ❗

Welcome to Enoch AI Strategy Bot 🚀

💚 Explore automated trading with multiple strategies, test everything on a Demo Account, and start in minutes.

❓ <b>What can this bot do?</b>

✅ Real Market Analysis (EMA9 + RSI)
✅ 3 Professional Sessions
   🌅 Morning: 10AM-11AM
   ☀️ Afternoon: 1PM-2PM
   🌙 Evening: 5PM-6PM
✅ No 12:60 bug - Perfect Timing
✅ Live Stats Tracking

<b>📊 TODAY STATS - {stats['date']}</b>
🌅 Morning: {stats['MORNING']} signals
☀️ Afternoon: {stats['AFTERNOON']} signals
🌙 Evening: {stats['EVENING']} signals
Total: {stats['MORNING']+stats['AFTERNOON']+stats['EVENING']} signals

🤖 <b>COMMANDS:</b>
/start - Show this menu
stats - Daily report
win / loss - Record result

🔥 Ready? Next session check below!
"""

PAIRS = ["EUR/USD OTC","Gold OTC","USD/JPY OTC","AUD/USD OTC","EUR/JPY OTC","GBP/JPY OTC","USD/CAD OTC","EUR/GBP OTC","USD/CHF OTC","AUD/JPY OTC","EUR/AUD OTC","BTC/USD OTC","EUR/CAD OTC","NZD/USD OTC","Silver OTC"]

# --- LISTEN FOR /start and stats ---
def command_listener():
    print("Command listener started")
    offset = 0
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            r = requests.get(url, params={"offset": offset, "timeout": 30}, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "").lower()
                chat_id = msg.get("chat", {}).get("id")
                if not text or
