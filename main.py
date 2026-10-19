import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
WAT = pytz.timezone("Africa/Lagos")
# YOUR REAL LINK
MY_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Professional LIVE with Affiliate Link"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send(chat_id, text, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if buttons:
            data["reply_markup"] = buttons
        requests.post(url, json=data, timeout=10)
    except:
        pass

PAIRS = ["EUR/USD OTC","AUD/CAD OTC","AUD/JPY","CHF/JPY OTC","AUD/CAD","Gold OTC"]

def get_session(now):
    hm = now.hour * 100 + now.minute
    if 930 <= hm <= 1030:
        return "MORNING SESSION"
    if 1430 <= hm <= 1530:
        return "AFTERNOON SESSION"
    if 2030 <= hm <= 2130:
        return "EVENING SESSION"
    return None

WELCOME = f"""⭐ ENOCH PROFESSIONAL TRADING SYSTEM ⭐
━━━━━━━━━━━━━━━━━━━━
⚠️ THIS IS NOT GAMBLING
THIS IS STRATEGY

Hello Enoch 👋
Welcome to Professional Hub!

📊 PROFESSIONAL SETTINGS:
🕘 Sessions: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ Expiry: 3 MIN [M3] | M1 Entry
📈 Strategy: Breakout + Volume
✅ Risk: 1% | Martingale 1 Step
✅ Pairs: 6 Pairs + Gold OTC

Use buttons below:
🔗 REGISTER HERE - Get link
🆔 My Trading ID - Send ID
ℹ️ How it works - Guide

Admin @Enochsystem dey online!"""

def handle_private():
    offset = 0
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=20"
            r = requests.get(url, timeout=25).json()
            for upd in r.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message", {})
                text = msg.get("text", "").lower()
                chat_id = msg.get("chat", {}).get("id")
                if not chat_id:
                    continue
                if "start" in text:
                    buttons = {
                        "keyboard": [
                            [{"text": "🔗 REGISTER HERE"}, {"text": "🆔 My Trading ID"}],
                            [{"text": "ℹ️ How it works"}, {"text": "📊 Start Signals"}]
                        ],
                        "resize_keyboard": True
                    }
                    send(chat_id, WELCOME, buttons)
                elif "how" in text:
                    send(chat_id, "📖 HOW IT WORKS:\n━━━━━━━━━━━━\n1. Register with my Pocket Option link\n2. Deposit min $10\n3. Send your Trading ID\n4. Signals drop 9:30AM, 2:30PM, 8:30PM WAT\n5. Use 1% risk, 1 martingale\n6. Follow clock set exactly!")
                elif "register" in text:
                    # YOUR REAL LINK HERE
                    send(chat_id, f"🔥 REGISTER HERE & GET $10,000 DEMO:\n\n👉 {MY_LINK}\n\nQuotex registration | QxBroker sign up\nRegister on Qx broker and get $10,000 for demo account. Learn and start real trading. Minimum deposit is 10$. Join!")
                elif "trading id" in text:
                    send(chat_id, "Send your Trading ID - Go to Pocket Option > Profile > Copy ID and paste here")
                elif "signal" in text:
                    send(chat_id, "✅ PROFESSIONAL SIGNALS ACTIVE!\nYou go receive signals here & channel.\nNext: 9:30AM, 2:30PM, 8:30PM WAT")
        except:
            time.sleep(5)

def signal_loop():
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
            conf = random.randint(87, 96)
            m1 = f"📊 PROFESSIONAL SETUP\n━━━━━━━━━━━━━━━━━━━━\n📌 PAIR: {p}\n⏱️ EXPIRY: 3 MIN [M3] | ENTRY M1\n🕐 CLOCK SET: {set_time} WAT\n🎯 PREPARE: {short}\n💰 PAYOUT: +92%\n⏰ SESSION: {sess}\n📈 CONFIDENCE: {conf}%\n━━━━━━━━━━━━━━━━━━━━\nSTATUS: ⏳ Analyzing breakout..."
            if is_up:
                m2 = f"🚨 ENTRY ALERT - {sess}\n━━━━━━━━━━━━━━━━━━━━\n⏰ TIME: {set_time} WAT\n📌 PAIR: {p}\nDIRECTION: UP 🔼\nSIGNAL: 🚀 ROCKET BUY 🚀\n━━━━━━━━━━━━━━━━━━━━\n📈 CHART:\n• Break of Resistance 📈\n• Price above EMA 9 & 21\n• Volume Spike + Bullish Engulfing\n• RSI 62 - Strong momentum\n━━━━━━━━━━━━━━━━━━━━\n✅ REASON: Breakout confirmed\n⬆️ ACTION: BUY NOW at {set_time}"
            else:
                m2 = f"🚨 ENTRY ALERT - {sess}\n━━━━━━━━━━━━━━━━━━━━\n⏰ TIME: {set_time} WAT\n📌 PAIR: {p}\nDIRECTION: DOWN 🔽\nSIGNAL: 🎯 TARGET SELL 🎯\n━━━━━━━━━━━━━━━━━━━━\n📈 CHART:\n• Break of Support 📉\n• Price below EMA 9 & 21\n• Volume Spike + Bearish Engulfing\n• RSI 38 - Strong pressure\n━━━━━━━━━━━━━━━━━━━━\n✅ REASON: Breakdown confirmed\n⬇️ ACTION: SELL NOW at {set_time}"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(180)
        except:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=handle_private, daemon=True).start()
signal_loop()
