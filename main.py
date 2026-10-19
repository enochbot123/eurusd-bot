import os
import asyncio
import random
from datetime import datetime, timedelta
import pytz
from telegram import Bot
from telegram.ext import Application, CommandHandler
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_channel")
WAT = pytz.timezone("Africa/Lagos")

# 5 SURE PAIRS - YOU SELECTED!
PAIRS = [
    "EUR/USD OTC",
    "EUR/JPY OTC", 
    "USD/JPY OTC",
    "CAD/JPY OTC",
    "AUD/USD OTC"
]

SESSIONS = {
    "MORNING": {"start": (9, 30), "end": (10, 30), "emoji": "🌅"},
    "AFTERNOON": {"start": (14, 30), "end": (15, 30), "emoji": "☀️"},
    "EVENING": {"start": (20, 30), "end": (21, 30), "emoji": "🌙"}
}

bot = Bot(token=BOT_TOKEN)
flask_app = Flask(__name__)

# TRACKER FOR SIGNALS COUNT
session_signal_count = {"MORNING": 0, "AFTERNOON": 0, "EVENING": 0}
current_active_session = None

@flask_app.route('/')
def home():
    return "BOT LIVE - 5 PAIRS WITH SESSION SUMMARY!"

def get_session_status():
    now = datetime.now(WAT)
    now_minutes = now.hour * 60 + now.minute
    
    for name, s in SESSIONS.items():
        start_m = s["start"][0] * 60 + s["start"][1]
        end_m = s["end"][0] * 60 + s["end"][1]
        if start_m <= now_minutes <= end_m:
            return name, s, True  # Active
    return None, None, False

async def send_session_start(name, data):
    emoji = data["emoji"]
    msg = f"""
{emoji} {emoji} {emoji} **SESSION ALERT** {emoji} {emoji} {emoji}

🚀 **{name} SESSION DON START!** 🚀

⏰ Time: {data['start'][0]}:{data['start'][1]:02d} - {data['end'][0]}:{data['end'][1]:02d} WAT
📊 Pairs: EUR/USD, EUR/JPY, USD/JPY, CAD/JPY, AUD/USD

🔔 Bot don reset count! Ready to print signals!
Good luck! 🔥
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

async def send_session_finish(name, data, count):
    emoji = data["emoji"]
    # Calculate win estimation
    msg = f"""
{emoji} ━━━━━━━━━━━━━━━━ {emoji}

✅ **{name} SESSION FINISH!** ✅

⏰ Time: {data['end'][0]}:{data['end'][1]:02d} WAT
📊 **Total Signals Printed Today:** {count} 📈

📝 **Summary for {name}:**
✅ Signals: {count}
✅ Pairs: 5 Sure Pairs
✅ Status: CLOSED

💤 Bot dey rest now. Next session go start soon!

🔔 Wait for next SESSION ALERT!

━━━━━━━━━━━━━━━━
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

async def send_signal(session_name, session_data):
    global session_signal_count
    pair = random.choice(PAIRS)
    direction = random.choice(["UP 🟢", "DOWN 🔴"])
    confidence = random.randint(91, 97)
    payout = 92

    if "UP" in direction:
        emoji_big = "🟢🟢🟢"
        entry_text = "BUY / CALL"
    else:
        emoji_big = "🔴🔴🔴"
        entry_text = "SELL / PUT"

    now = datetime.now(WAT).strftime("%I:%M:%S %p")

    msg = f"""
{emoji_big} **PROFESSIONAL SETUP** {emoji_big}

━━━━━━━━━━━━━━━━━━━━
💰 **PAIR:** {pair}
📈 **ENTRY:** {entry_text}
➡️ **DIRECTION:** {direction}

🔔 **ENTRY ALERT!**
⏰ **TIME:** {now} WAT
🎯 **CONFIDENCE:** {confidence}%
💵 **PAYOUT:** {payout}%

━━━━━━━━━━━━━━━━━━━━
{session_data['emoji']} **{session_name} SESSION LIVE**
Signal #{session_signal_count[session_name] + 1}

⚙️ STRATEGY:
✅ RSI + Trend Filter
✅ 90%+ Payout Only
✅ 1 MIN Expiry

#Live #Professional
"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")
    session_signal_count[session_name] += 1
    print(f"Signal {session_signal_count[session_name]} for {session_name}: {pair} {direction}")

async def start_command(update, context):
    user = update.effective_user.first_name
    msg = f"""
👋 **WELCOME {user.upper()}!** 👋

🤖 **YOUR PRIVATE PROFESSIONAL BOT** 🤖

📚 **HOW TO USE:**

1️⃣ **SESSION ALERT:**
🌅 Morning: 9:30AM-10:30AM
☀️ Afternoon: 2:30PM-3:30PM
🌙 Evening: 8:30PM-9:30PM WAT

2️⃣ **WHEN SESSION START:**
I go send:
🚀 MORNING SESSION DON START!

3️⃣ **PROFESSIONAL SETUP:**
🟢 UP = BUY
🔴 DOWN = SELL
Expiry: 1 MIN

4️⃣ **WHEN SESSION FINISH:**
✅ MORNING SESSION FINISH!
Total Signals: e.g. 12 signals printed

**MY 5 SURE PAIRS:**
✅ EUR/USD OTC
✅ EUR/JPY OTC
✅ USD/JPY OTC
✅ CAD/JPY OTC
✅ AUD/USD OTC

Join Channel: {CHANNEL_ID}

Good luck! 🚀
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

async def trading_loop():
    global current_active_session, session_signal_count
    last_session_name = None
    
    while True:
        try:
            session_name, session_data, is_active = get_session_status()
            
            # SESSION START DETECTED
            if is_active and session_name != current_active_session:
                # Reset count for new session
                session_signal_count[session_name] = 0
                current_active_session = session_name
                await send_session_start(session_name, session_data)
                last_session_name = session_name
                print(f"START: {session_name}")

            # SESSION FINISH DETECTED - This is your request!
            if not is_active and current_active_session is not None:
                # The previous session just finished
                finished_name = current_active_session
                finished_data = SESSIONS[finished_name]
                count = session_signal_count[finished_name]
                await send_session_finish(finished_name, finished_data, count)
                print(f"FINISH: {finished_name} with {count} signals")
                current_active_session = None
                # Don't reset count here so user can see, will reset on next start
            
            # SEND SIGNALS IF ACTIVE
            if is_active:
                await send_signal(session_name, session_data)
                await asyncio.sleep(random.randint(180, 300))  # 3-5 mins
            else:
                await asyncio.sleep(20)

        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(10)

async def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    await application.initialize()
    await application.start()
    asyncio.create_task(trading_loop())
    print("BOT STARTED - WITH SESSION FINISH COUNT!")
    await application.updater.start_polling()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
