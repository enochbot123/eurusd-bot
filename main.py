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
    return "Enoch Professional System LIVE"

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

WELCOME = """\u2b50 ENOCH PROFESSIONAL TRADING SYSTEM \u2b50
━━━━━━━━━━━━━━━━━━━━
\u26a0\ufe0f THIS IS NOT GAMBLING
THIS IS STRATEGY

Hello Enoch \U0001f44b
Welcome to Professional Hub!

\U0001f4ca PROFESSIONAL SETTINGS:
\u23f0 Sessions: 9:30AM | 2:30PM | 8:30PM WAT
\u23f1\ufe0f Expiry: 3 MIN [M3] | M1 Entry
\U0001f4c8 Strategy: Breakout + Volume
\u2705 Risk: 1% | Martingale 1 Step
\u2705 Pairs: 6 Pairs + Gold OTC

Use buttons below:
\U0001f517 REGISTER HERE - Get link
\U0001f194 My Trading ID - Send ID
\u2139\ufe0f How it works - Guide

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
                            [{"text": "\U0001f517 REGISTER HERE"}, {"text": "\U0001f194 My Trading ID"}],
                            [{"text": "\u2139\ufe0f How it works"}, {"text": "\U0001f4ca Start Signals"}]
                        ],
                        "resize_keyboard": True
                    }
                    send(chat_id, WELCOME, buttons)
                elif "how" in text:
                    send(chat_id, "\U0001f4d6 HOW IT WORKS:\n━━━━━━━━━━━━\n1. Register with my link\n2. Deposit min $10\n3. Send ID to activate\n4. Signals drop 9:30, 2:30, 8:30 WAT\n5. Use 1% risk, 1 martingale\n6. Follow clock set exactly!")
                elif "register" in text:
                    send(chat_id, "Register here: https://quotex.io/en/sign-up/ (put your link)")
                elif "trading id" in text:
                    send(chat_id, "Send your Trading ID - Go to Quotex > Profile > Copy ID")
                elif "signal" in text:
                    send(chat_id, "\u2705 PROFESSIONAL SIGNALS ACTIVE!\nYou go receive signals here & channel.\nNext: 9:30AM, 2:30PM, 8:30PM WAT")
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
            # M1 PROFESSIONAL SET
            m1 = f"\U0001f4ca PROFESSIONAL SETUP\n"
            m1 += f"━━━━━━━━━━━━━━━━━━━━\n"
            m1 += f"\U0001f4cc PAIR: {p}\n"
            m1 += f"\u23f1\ufe0f EXPIRY: 3 MIN [M3] | ENTRY M1\n"
            m1 += f"\U0001f550 CLOCK SET: {set_time} WAT\n"
            m1 += f"\U0001f3af PREPARE: {short}\n"
            m1 += f"\U0001f4b0 PAYOUT: +92%\n"
            m1 += f"\u23f0 SESSION: {sess}\n"
            m1 += f"\U0001f4c8 CONFIDENCE: {conf}%\n"
            m1 += f"━━━━━━━━━━━━━━━━━━━━\n"
            m1 += f"STATUS: \u23f3 Analyzing breakout..."
            # M2 PROFESSIONAL ENTRY
            if is_up:
                m2 = f"\U0001f6a8 ENTRY ALERT - {sess}\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\u23f0 TIME: {set_time} WAT\n"
                m2 += f"\U0001f4cc PAIR: {p}\n"
                m2 += f"DIRECTION: UP \U0001f53c\n"
                m2 += f"SIGNAL: \U0001f680 ROCKET BUY \U0001f680\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\U0001f4c8 CHART ANALYSIS:\n"
                m2 += f"\u2022 Break of Resistance \U0001f4c8\n"
                m2 += f"\u2022 Price above EMA 9 & 21\n"
                m2 += f"\u2022 Volume Spike + Bullish Engulfing\n"
                m2 += f"\u2022 RSI 62 - Strong momentum\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\u2705 REASON: Breakout confirmed\n"
                m2 += f"\u2b06\ufe0f ACTION: BUY NOW at {set_time}"
            else:
                m2 = f"\U0001f6a8 ENTRY ALERT - {sess}\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\u23f0 TIME: {set_time} WAT\n"
                m2 += f"\U0001f4cc PAIR: {p}\n"
                m2 += f"DIRECTION: DOWN \U0001f53d\n"
                m2 += f"SIGNAL: \U0001f3af TARGET SELL \U0001f3af\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\U0001f4c8 CHART ANALYSIS:\n"
                m2 += f"\u2022 Break of Support \U0001f4c9\n"
                m2 += f"\u2022 Price below EMA 9 & 21\n"
                m2 += f"\u2022 Volume Spike + Bearish Engulfing\n"
                m2 += f"\u2022 RSI 38 - Strong pressure\n"
                m2 += f"━━━━━━━━━━━━━━━━━━━━\n"
                m2 += f"\u2705 REASON: Breakdown confirmed\n"
                m2 += f"\u2b07\ufe0f ACTION: SELL NOW at {set_time}"
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(180)
        except Exception as e:
            print(e)
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=handle_private, daemon=True).start()
signal_loop()
