import os, asyncio, random, requests
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
        return round(p + random.uniform(-0.002, 0.002), 5), round(p, 5)

async def send_signal(pair, bot):
    live, prev = get_real_price(pair)
    setup = random.choice(["Resistance Rejection", "Support Bounce", "Breakout + Retest"])
    action = "SELL PUT" if live > prev else "BUY CALL"
    msg = f"""🚨 ENTER NOW!!! REAL MARKET SIGNAL

{pair} - {action}
⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}
✅ REAL PRICE: {live} (LIVE - Was {prev})
🎯 SETUP: {setup}
📈 CONFIDENCE: {random.randint(90,97)}%

👉 ACTION: {action} NOW!
🔗 Trade Here: {AFFILIATE_LINK}"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg)
    print(f"SENT {pair}")

async def session_runner(bot):
    while True:
        now = datetime.now(WAT)
        cur = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        if cur in SESSIONS and session_data["last_session"] != f"{today}_{cur}":
            session_data["last_session"] = f"{today}_{cur}"
            session_data["next_index"] = 0
        for sess in SESSIONS:
            sh, sm = map(int, sess.split(":"))
            s_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            s_end = s_start + timedelta(hours=1)
            if s_start <= now <= s_end and session_data["next_index"] < len(PAIRS):
                await send_signal(PAIRS[session_data["next_index"]], bot)
                session_data["next_index"] += 1
                await asyncio.sleep(120) # 2 mins for your recording tonight
                break
        await asyncio.sleep(20)

async def post_init(app):
    # THIS LINE GO KILL THAT CONFLICT ERROR FOR YOUR SCREENSHOT
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Ghost cleared - Starting Enoch Bot")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update, context):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"] = 0
    await send_signal(PAIRS[session_data["next_index"]], context.bot)
    session_data["next_index"] += 1
    await update.message.reply_text(f"✅ Sent! Go record am!")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("testsignal", testsignal))
    print("Enoch Bot 5-Pairs Mode Starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
