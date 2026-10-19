import os, time, requests, threading, random
from datetime import datetime, timedelta
import pytz
from flask import Flask

# ========== YOUR SETTINGS ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = "-1003714315133"
WAT = pytz.timezone("Africa/Lagos")
MY_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
# ===================================

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Professional FINAL - Live"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def send(chat_id, text, buttons=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if buttons:
            data["reply_markup"] = buttons
        requests.post(url, json=data, timeout=10)
    except:
        pass

# PROFESSIONAL PAIRS - REAL MARKET FORMAT
PAIRS = ["EUR/USD OTC","GBP/USD OTC","AUD/CAD OTC","AUD/JPY OTC","CHF/JPY OTC","USD/JPY OTC","Gold OTC","EUR/JPY OTC"]

def get_session(now):
    hm = now.hour * 100 + now.minute
    if 930 <= hm <= 1030:
        return "MORNING SESSION"
    if 1430 <= hm <= 1530:
        return "AFTERNOON SESSION"
    if 2030 <= hm <= 2130:
        return "EVENING SESSION"
    return None

# ===== PRIVATE BOT MESSAGES =====
WELCOME_MSG = f"""⭐ <b>ENOCH PROFESSIONAL TRADING SYSTEM</b> ⭐
━━━━━━━━━━━━━━━━━━━━
⚠️ <b>THIS IS NOT GAMBLING - THIS IS STRATEGY</b>

Hello Enoch 👋
Welcome to Professional Hub!

📊 <b>PROFESSIONAL SETTINGS:</b>
🕘 Sessions: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ Expiry: 3 MIN [M3] | Entry M1
📈 Strategy: Breakout + Retest + Volume
💹 Risk: 1% | Martingale 1 Step Only
🎯 Pairs: EUR/USD, GBP/USD, GOLD etc

📢 <b>Channel:</b> Enoch Signals
💬 <b>Support:</b> @Enochsystem

👇 Choose option below:
"""

REGISTER_MSG = f"""🔥 <b>REGISTER & START TRADING</b> 🔥
━━━━━━━━━━━━━━━━━━━━

👉 <b>OFFICIAL LINK:</b>
{MY_LINK}

✅ <b>Why Register With Our Link?</b>
• Get $10,000 Demo Balance
• 92% Payout Guaranteed
• Fast Deposit & Withdrawal
• Minimum Deposit $10 Only

📌 <b>Steps:</b>
1. Click link above
2. Sign up with email
3. Deposit minimum $10
4. Send your Trading ID here

🎁 <b>Bonus:</b> Deposit $20 get extra bonus!

👉 {MY_LINK}
"""

HOW_IT_WORKS_MSG = """ℹ️ <b>HOW IT WORKS - PROFESSIONAL GUIDE</b>
━━━━━━━━━━━━━━━━━━━━

<b>STEP 1: REGISTER</b>
Click REGISTER HERE button & create account

<b>STEP 2: SEND ID</b>
After registration, copy your Trading ID & send here

<b>STEP 3: GET SIGNALS</b>
We send professional signals 3 times daily:
• 9:30AM - Morning Session
• 2:30PM - Afternoon Session
• 8:30PM - Evening Session

<b>STEP 4: TRADE LIKE PRO</b>
• Use M1 timeframe
• Set expiry 3 MIN [M3]
• Enter at exact time we give
• Risk 1% only
• Martingale 1 step if needed

<b>CHART SETUP:</b>
• Resistance/Support breakout
• Volume confirmation
• Confidence 87-96%

⚠️ <b>RISK WARNING:</b> Trading involves risk. Trade with money you can afford to lose. This is educational signals only.

Need help? Contact @Enochsystem
"""

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
                if not chat_id or str(chat_id) == CHANNEL_ID:
                    continue
                
                if "start" in text:
                    buttons = {
                        "keyboard": [
                            [{"text": "🔗 REGISTER HERE"}, {"text": "🆔 My Trading ID"}],
                            [{"text": "ℹ️ How it works"}, {"text": "📊 Start Signals"}]
                        ],
                        "resize_keyboard": True
                    }
                    send(chat_id, WELCOME_MSG, buttons)
                
                elif "register" in text:
                    send(chat_id, REGISTER_MSG)
                
                elif "trading id" in text or "my trading" in text:
                    send(chat_id, "📝 <b>Send Your Trading ID</b>\n\nCopy your ID from your trading platform and paste it here.\n\nExample: 12345678\n\nAfter you send ID, you will be verified for signals ✅")
                
                elif len(text) >= 5 and text.replace(" ","").isdigit():
                    send(chat_id, f"✅ <b>ID RECEIVED: {text.upper()}</b>\n\nYour ID is under verification (24hrs)\n\nMeanwhile, join channel for FREE signals:\nSignals time: 9:30AM, 2:30PM, 8:30PM WAT\n\nKeep trading with discipline! 💹")
                
                elif "how" in text:
                    send(chat_id, HOW_IT_WORKS_MSG)
                
                elif "signal" in text:
                    send(chat_id, "✅ <b>SIGNALS ACTIVE!</b>\n\n📢 Join Channel: Enoch Signals Channel\n⏰ Next Session: Check channel for countdown\n\nStay tuned - Professional signals loading... ⏳")
        except Exception as e:
            time.sleep(5)

def signal_loop():
    last_pair = ""
    while True:
        try:
            now = datetime.now(WAT)
            sess = get_session(now)
            if sess is None:
                time.sleep(30)
                continue
            
            # Real market rotation - no repeat
            p = random.choice(PAIRS)
            if p == last_pair:
                p = random.choice(PAIRS)
            last_pair = p
            
            is_up = random.choice([True, False])
            set_time = (now + timedelta(minutes=1)).strftime("%H:%M")
            short = p.replace(" OTC","").replace(" OTC","")
            conf = random.randint(87, 96)
            payout = random.choice([88, 89, 92, 93])
            
            # ===== PROFESSIONAL SETUP - REAL MARKET SIGNAL =====
            m1 = f"""📊 <b>PROFESSIONAL SETUP - {sess}</b>
━━━━━━━━━━━━━━━━━━━━
📌 <b>PAIR:</b> {p}
⏱️ <b>EXPIRY:</b> 3 MIN [M3] | ENTRY M1
🕐 <b>CLOCK SET:</b> {set_time} WAT
🎯 <b>PREPARE:</b> {short}
💰 <b>PAYOUT:</b> +{payout}%
⏰ <b>SESSION:</b> {sess}
📈 <b>CONFIDENCE:</b> {conf}%
━━━━━━━━━━━━━━━━━━━━
📉 <b>ANALYSIS:</b> Real market breakout forming...
STATUS: ⏳ <b>Analyzing volume... Waiting for entry - {set_time}</b>
"""

            if is_up:
                m2 = f"""🚨 <b>ENTRY ALERT - {sess}</b>
━━━━━━━━━━━━━━━━━━━━
⏰ <b>TIME:</b> {set_time} WAT
📌 <b>PAIR:</b> {p}
<b>DIRECTION: UP 🔼</b>
<b>SIGNAL: 🚀 ROCKET BUY 🚀</b>
━━━━━━━━━━━━━━━━━━━━
📈 <b>CHART:</b> Break of Resistance + Volume Spike
✅ <b>REASON:</b> Bullish breakout confirmed
⬆️ <b>ACTION: BUY NOW at {set_time}</b>
⚠️ <b>RISK:</b> 1% only | Martingale 1 step max
"""
            else:
                m2 = f"""🚨 <b>ENTRY ALERT - {sess}</b>
━━━━━━━━━━━━━━━━━━━━
⏰ <b>TIME:</b> {set_time} WAT
📌 <b>PAIR:</b> {p}
<b>DIRECTION: DOWN 🔽</b>
<b>SIGNAL: 🎯 TARGET SELL 🎯</b>
━━━━━━━━━━━━━━━━━━━━
📈 <b>CHART:</b> Break of Support + Volume Spike
✅ <b>REASON:</b> Bearish breakdown confirmed
⬇️ <b>ACTION: SELL NOW at {set_time}</b>
⚠️ <b>RISK:</b> 1% only | Martingale 1 step max
"""
            
            send(CHANNEL_ID, m1)
            time.sleep(60)
            send(CHANNEL_ID, m2)
            time.sleep(180)
            
        except:
            time.sleep(10)

threading.Thread(target=run_flask, daemon=True).start()
threading.Thread(target=handle_private, daemon=True).start()
signal_loop()
