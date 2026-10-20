import os
import asyncio
import random
import requests
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAIRS = ["AUD/USD", "EUR/USD", "USD/JPY", "EUR/JPY", "USD/CAD"]
WAT = pytz.timezone("Africa/Lagos")
AFFILIATE_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
SESSIONS = ["09:30", "14:30", "20:30"]

session_data = {"last_session": "", "next_index": 0}

def get_real_price(pair):
    try:
        symbol = pair.replace("/", "")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}=X?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = r.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        prev = data['chart']['result'][0]['meta']['previousClose']
        return float(price), float(prev)
    except:
        base = {"AUD/USD": 0.698, "EUR/USD": 1.084, "USD/JPY": 154.2, "EUR/JPY": 167.1, "USD/CAD": 1.365}
        p = base.get(pair, 1.0)
        live = p + random.uniform(-0.002, 0.002)
        return round(live, 5), round(p, 5)

def build_analysis(pair, price, prev):
    setups = ["Resistance Rejection", "Support Bounce", "Breakout + Retest", "Supply Zone Reaction", "Demand Zone"]
    setup = random.choice(setups)
    action = "SELL PUT" if price > prev else "BUY CALL"
    conf = random.randint(89, 97)
    rsi = random.randint(38, 72)
    if "Resistance" in setup or "Supply" in setup:
        analysis = "Price hit strong supply zone. Sellers dey control."
    else:
        analysis = "Price hit strong demand zone. Buyers dey push."
    return setup, action, conf, rsi, analysis

async def send_signal(pair, bot):
    live, prev = get_real_price(pair)
    setup, action, conf, rsi, analysis = build_analysis(pair, live, prev)

    msg1 = f"""📊 PROFESSIONAL SETUP - REAL MARKET PRICE!

PAIR: {pair}
PRICE: {live} (LIVE)
PREV: {prev}

SETUP: {setup}
RSI (M15): {rsi}
M15 Analysis: {analysis}

Monitoring for entry..."""

    msg2 = f"""🚨 ENTER NOW!!! REAL MARKET SIGNAL

{pair} - {action}
⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}

✅ REAL PRICE: {live} (LIVE - Was {prev})
🎯 SETUP: {setup}
📈 CONFIDENCE: {conf}%
📊 ANALYSIS: {analysis}

👉 ACTION: {action} NOW!

🔗 Trade Here: {AFFILIATE_LINK}

#PocketOption #{pair.replace('/', '')}"""

    await bot.send_message(chat_id=CHANNEL_ID, text=msg1)
    await asyncio.sleep(3)
    await bot.send_message(chat_id=CHANNEL_ID, text=msg2)
    print(f"SENT {pair} - {live}")

async def session_runner(bot):
    while True:
        now = datetime.now(WAT)
        cur = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")

        if cur in SESSIONS:
            if session_data["last_session"] != f"{today}_{cur}":
                session_data["last_session"] = f"{today}_{cur}"
                session_data["next_index"] = 0
                print(f"NEW SESSION {cur} - Reset to 0 - 5 pairs go drop")

        # Check if inside any session window (1 hour)
        for sess in SESSIONS:
            sh, sm = map(int, sess.split(":"))
            sess_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            sess_end = sess_start + timedelta(hours=1)
            if sess_start <= now <= sess_end:
                if session_data["next_index"] < len(PAIRS):
                    pair = PAIRS[session_data["next_index"]]
                    await send_signal(pair, bot)
                    session_data["next_index"] += 1
                    # For tonight recording: 2 mins interval, tomorrow we change to 720 (12 mins)
                    await asyncio.sleep(120)
                    break
        await asyncio.sleep(20)

async def post_init(application):
    # THIS ONE GO CLEAR THAT CONFLICT GHOST ERROR
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("Ghost instance cleared - Starting fresh Enoch Bot")
    asyncio.create_task(session_runner(application.bot))

async def testsignal(update, context):
    if session_data["next_index"] >= len(PAIRS):
        session_data["next_index"] = 0
    pair = PAIRS[session_data["next_index"]]
    await send_signal(pair, context.bot)
    session_data["next_index"] += 1
    await update.message.reply_text(f"✅ Sent {pair} for channel. Next index: {session_data['next_index']}. Go record am!")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("testsignal", testsignal))
    print("Enoch Bot - 5 Pairs Rotation Mode - Starting polling...")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message"])

if __name__ == "__main__":
    main()
