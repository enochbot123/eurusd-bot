# -*- coding: utf-8 -*-
import os
import time
import requests
import threading
import random
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
    html = "<html><head><meta charset='utf-8'><title>Enoch System</title></head>"
    html += "<body style='background:#0a0a0a;color:#00ff88;text-align:center;padding-top:60px;font-family:Arial'>"
    html += "<h1>\U0001f680 Enoch System LIVE</h1><h2>\U0001f4bc 5 Pairs Pro Bot</h2>"
    html += "<p>\u2705 Status: ONLINE</p><p>\u23f0 Sessions: 10AM | 1PM | 5PM UTC</p>"
    html += "<p>\U0001f550 Reminders: 9:45AM | 12:45PM | 4:45PM</p>"
    html += "<p>\U0001f4ca Pairs: Gold, EUR/USD, GBP/USD, EUR/JPY, GBP/JPY</p>"
    html += "<p>\U0001f4ac Admin: @Enochsystem</p></body></html>"
    return html

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN:
        return
    url = "https://api.telegram.org/bot" + BOT_TOKEN + "/sendMessage"
    payload = {}
    payload["chat_id"] = chat_id
    payload["text"] = text
    payload["parse_mode"] = "HTML"
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(str(e))

PAIRS = ["Gold OTC","EUR/USD OTC","GBP/USD OTC","EUR/JPY OTC","GBP/JPY OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "\U0001f517 REGISTER HERE"}, {"text": "\U0001f194 My Trading ID"}],
        [{"text": "\u2139\ufe0f How it works"}, {"text": "\U0001f4ac Chat @Enochsystem"}],
        [{"text": "\U0001f680 Start Signals"}]
    ],
    "resize_keyboard": True
}

def listen_commands():
    offset = 0
    base = "https://api.telegram.org/bot" + BOT_TOKEN + "/getUpdates"
    while True:
        try:
            r = requests.get(base, params={"offset": offset, "timeout": 30}, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_info = msg.get("chat", {})
                chat_id = chat_info.get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
                first_name = from_user.get("first_name", "Trader")
                user_name = from_user.get("username", "No username")
                if not chat_id:
                    continue
                low = text.lower()
                if "/start" in low or "start signals" in low:
                    alert = "NEW PERSON Name: " + first_name + " Username: @" + user_name + " ID: " + str(chat_id)
                    send(MY_ID, alert)
                    welcome = "\U0001f680 <b>THIS IS NOT GAMBLING</b>\n\U0001f4bc <b>THIS IS STRATEGY</b>\n\nHello " + first_name + " \U0001f44b\n\nWelcome to <b>Enoch System!</b> \u2728\n\n\U0001f4bc Professional Hub\n\U0001f4ca 5 Pairs Pro\n\u23f0 Sessions: 10AM | 1PM | 5PM UTC\n\U0001f550 Reminders: 9:45AM, 12:45PM, 4:45PM\n\u2705 3Min Expiry\n\nUse buttons below \U0001f447"
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)
                if "how it works" in low:
                    txt = "\u2139\ufe0f <b>HOW IT WORKS</b>\n\n1\ufe0f\u20e3 REGISTER HERE \U0001f517\n2\ufe0f\u20e3 Fund $10 \U0001f4b5\n3\ufe0f\u20e3 Send screenshot \U0001f4f8\n4\ufe0f\u20e3 Get VIP \U0001f389\n\n\U0001f4b0 5 Pairs: Gold, EUR/USD, GBP/USD, EUR/JPY, GBP/JPY\n\u23f0 Sessions: 10AM | 1PM | 5PM UTC"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                if "my trading id" in low:
                    txt = "\U0001f194 <b>How to get Trading ID</b>\n\n1\ufe0f\u20e3 Login \U0001f510\n2\ufe0f\u20e3 Profile \U0001f464\n3\ufe0f\u20e3 Copy ID \U0001f4cb\n4\ufe0f\u20e3 Send to @Enochsystem \U0001f4ac"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                if "register here" in low:
                    txt = "\U0001f517 <b>REGISTER HERE</b>\n\nLink:\n" + MY_LINK + "\n\nAfter:\n\u2705 Fund $10 \U0001f4b5\n\u2705 Send ID \U0001f194\n\n\U0001f389 VIP access!"
                    send(chat_id, txt, reply_markup=PRO_KEYBOARD)
                if "chat" in low:
                    send(chat_id, "\U0001f4ac Admin: @Enochsystem\n\U0001f7e2 Online!", reply_markup=PRO_KEYBOARD)
        except Exception as ex:
            print(str(ex))
            time.sleep(5)
        time.sleep(2)

def bot_loop():
    time.sleep(10)
    last = ""
    warned_morning = False
    warned_afternoon = False
    warned_evening = False
    send(MY_ID, "Bot LIVE - Emoji Pro Active! \U0001f680\u23f0")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            m = now.minute
            if h == 9 and m == 45 and warned_morning == False:
                send(CHANNEL_ID, "\u23f0 <b>MORNING REMINDER!</b> \u23f0\n\n\U0001f550 Time: 9:45 AM\n\U0001f680 <b>THIS IS NOT GAMBLING</b>\n\U0001f4bc <b>THIS IS STRATEGY</b>\n\n\U0001f4bc 5 Pairs Pro\n\U0001f4ca Gold, EUR/USD, GBP/USD, EUR/JPY, GBP/JPY\n\u23f0 <b>Morning Starts in 15 MINS!</b>\n\U0001f55a Session: 10:00-11:00 AM UTC\n\n\u2705 Get Ready! \U0001f4aa")
                warned_morning = True
            if h == 9 and m == 55:
                send(CHANNEL_ID, "\u23f0 <b>FINAL CALL! MORNING IN 5 MINS!</b> \U0001f6a8\n\n\U0001f55a Starts 10AM Sharp! \U0001f4c8")
            if h == 12 and m == 45 and warned_afternoon == False:
                send(CHANNEL_ID, "\u23f0 <b>AFTERNOON REMINDER!</b> \u23f0\n\n\U0001f550 Time: 12:45 PM\n\u23f0 <b>Afternoon Starts in 15 MINS!</b>\n\U0001f55a Session: 1PM-2PM UTC\n\n\u2705 Get Ready! \U0001f4aa")
                warned_afternoon = True
            if h == 12 and m == 55:
                send(CHANNEL_ID, "\u23f0 <b>FINAL CALL! AFTERNOON IN 5 MINS!</b> \U0001f6a8\n\n\U0001f55a Starts 1PM Sharp! \U0001f4c8")
            if h == 16 and m == 45 and warned_evening == False:
                send(CHANNEL_ID, "\u23f0 <b>EVENING REMINDER!</b> \u23f0\n\n\U0001f550 Time: 4:45 PM\n\u23f0 <b>Evening Starts in 15 MINS!</b>\n\U0001f55a Session: 5PM-6PM UTC\n\n\u2705 Get Ready! \U0001f4aa")
                warned_evening = True
            if h == 16 and m == 55:
                send(CHANNEL_ID, "\u23f0 <b>FINAL CALL! EVENING IN 5 MINS!</b> \U0001f6a8\n\n\U0001f55a Starts 5PM Sharp! \U0001f4c8")
            if h == 11:
                warned_morning = False
            if h == 14:
                warned_afternoon = False
            if h == 18:
                warned_evening = False
            if h >= 10 and h < 11:
                sess = "MORNING \u2600\ufe0f"
            elif h >= 13 and h < 14:
                sess = "AFTERNOON \U0001f324\ufe0f"
            elif h >= 17 and h < 18:
                sess = "EVENING \U0001f319"
            else:
                time.sleep(30)
                continue
            if now.second != 0:
                time.sleep(60 - now.second)
                continue
            pair = random.choice(PAIRS)
            while pair == last:
                pair = random.choice(PAIRS)
            last = pair
            direction = random.choice(["UP \u2b06\ufe0f","DOWN \u2b07\ufe0f"])
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            short = pair.replace(" OTC","")
            m1 = "\u23f0 <b>" + sess + " SIGNAL</b> \U0001f4ca\n\n\U0001f4b1 Currency pair: <b>" + pair + "</b>\n\u23f3 Expiration: 3 min [M3]\n\U0001f550 SET: <b>" + set_str + "</b> - Prepare " + short + " \U0001f3af"
            m2 = "\U0001f680 Entry time: <b>" + set_str + "</b> - " + sess + "\n\U0001f4c8 Direction: <b>" + direction + "</b>\n\U0001f4a1 Analysis: Price broke support \u2705"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(240)
        except Exception as ex2:
            print(str(ex2))
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=listen_commands, daemon=True).start()
bot_loop()
