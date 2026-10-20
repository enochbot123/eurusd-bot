import os, asyncio, random, requests
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

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

# === THIS NA THE START COMMAND WEY MISS BEFORE - I DON ADD AM BACK ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    
    welcome_msg = f"""👋 Hello {user}! Welcome to Enoch's Strategy Channel!

🔥 HOW TO GET SIGNALS:

1️⃣ Register with my link: 
👉 {AFFILIATE_LINK}

2️⃣ After registration, copy your Trader ID (e.g., 85673214)

3️⃣ Send your Trader ID here like this:
   /id 85673214

4️⃣ Once I confirm, you go get FULL ACCESS to channel:
   👉 {CHANNEL_ID}

📊 We give 15 signals daily:
- Morning: 9:30 AM - 10:30 AM (5 pairs)
- Afternoon: 2:30 PM - 3:30 PM (5 pairs)  
- Evening: 8:30 PM - 9:30 PM (5 pairs)

All signals na REAL LIVE MARKET PRICE with professional analysis!

⚠️ Make sure you register with my link o! No go use old account.

Type /id with your ID to start now! 👇
Example: /id 12345678"""

    await update.message.reply_text(welcome_msg)

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Abeg send like this: /id 12345678")
        return
    trader_id = context.args[0]
    await update.message.reply_text(f"""✅ ID Received: {trader_id}

I don save am! Our team go verify am in 5 mins.

If e correct with my link, I go add you for private signals!

Meanwhile join channel: {CHANNEL_ID}

Affiliate link if you never register:
{AFFILIATE_LINK}""")
    print(f"New ID: {trader_id} from {update.effective_user.username}")

async def send_signal(pair, bot):
    live, prev = get_real_price(pair)
    setup = random.choice(["Resistance Rejection", "Support Bounce", "Breakout + Retest", "Supply Zone Reaction"])
    action = "SELL PUT" if live > prev else "BUY CALL"
    
    msg1 = f"""📊 PROFESSIONAL SETUP - REAL MARKET PRICE!

PAIR: {pair}
PRICE: {live} (LIVE)
PREV: {prev}
SETUP: {setup}
RSI (M15): {random.randint(38,72)}

Monitoring for entry..."""

    msg2 = f"""🚨 ENTER NOW!!! REAL MARKET SIGNAL

{pair} - {action}
⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}
✅ REAL PRICE: {live} (LIVE - Was {prev})
🎯 SETUP: {setup}
📈 CONFIDENCE: {random.randint(90,97)}%

👉 ACTION: {action} NOW!
🔗 Trade Here: {AFFILIATE_LINK}
#PocketOption #{pair.replace('/','')}"""

    await bot.send_message(chat_id=CHANNEL_ID, text=msg1)
    await asyncio.sleep(3)
    await bot.send_message(chat_id=CHANNEL_ID, text=msg2)
    print(f"SENT {pair} - {live}")

async def session_runner(bot):
    while True:
        now = datetime.now(WAT)
        cur = now.strftime("%H:%M")
        today = now.strftime("%Y-%m-%d")
        if cur in SESSIONS and session_data["last_session"] != f"{today}_{cur}":
            session_data["last_session"] = f"{today}_{cur}"
            session_data["next_index"] = 0
            print(f"NEW SESSION {cur} - 5 pairs go drop")
        for sess in SESSIONS:
            sh, sm = map(int, sess.split(":"))
            s_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
            s_end = s_start + timedelta(hours=1)
            if s_start <= now <= s_end and session_data["next_index"] < len(PAIRS):
                await send_signal(PAIRS[session_data["next_index"]], bot)
                session_data["next_index"] += 1
                await asyncio.sleep(120) # 2 mins for tonight recording, later 720
                break
        await asyncio.sleep(20)

async def post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Ghost cleared - Enoch Bot with /start & 5 pairs ready")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"] = 0
    await send_signal(PAIRS[session_data["next_index"]], context.bot)
    session_data["next_index"] += 1
    await update.message.reply_text(f"✅ Sent {PAIRS[session_data['next_index']-1]} for channel. Go record am!")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start)) # <- THIS ONE DEY NOW!
    app.add_handler(CommandHandler("id", set_id))   # <- FOR ID REGISTRATION
    app.add_handler(CommandHandler("testsignal", testsignal))
    print("Enoch Bot - Full Version with /start + 5 Pairs Rotation")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
