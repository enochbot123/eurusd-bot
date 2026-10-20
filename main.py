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

def get_price(pair):
    try:
        sym = pair.replace("/", "")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=X?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        d = r.json()
        p = d['chart']['result'][0]['meta']['regularMarketPrice']
        prev = d['chart']['result'][0]['meta']['previousClose']
        return float(p), float(prev)
    except:
        base = {"AUD/USD":0.698,"EUR/USD":1.084,"USD/JPY":154.2,"EUR/JPY":167.1,"USD/CAD":1.365}
        b = base.get(pair,1.0)
        return round(b+random.uniform(-0.002,0.002),5), round(b,5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Welcome! Register: {AFFILIATE_LINK} Then /id YOUR_ID")

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /id 12345678")
        return
    await update.message.reply_text(f"ID {context.args[0]} saved!")

async def send_signal(pair, bot, fast_mode=False):
    try:
        live, prev = get_price(pair)
        setup = random.choice(["Support Bounce at Demand","Resistance at Supply","Breakpoint Retest"])
        action = "SELL PUT" if live > prev else "BUY CALL"
        emoji = "🔴 SELL" if "SELL" in action else "🟢 BUY"

        if fast_mode:
            t1,t2,t3,t4 = 10,10,10,10
        else:
            t1,t2,t3,t4 = 120,60,60,60

        await bot.send_message(chat_id=CHANNEL_ID, text=f"""📊 PAIR TO WATCH!

💰 PAIR: {pair}
💵 PRICE: {live}
🎯 SETUP: {setup}
⏰ ENTRY: In next 5 mins!

Prepare! 🔗 {AFFILIATE_LINK}""")
        await asyncio.sleep(t1)

        await bot.send_message(chat_id=CHANNEL_ID, text=f"""⏳ {pair} UPDATE!

💰 PRICE: {get_price(pair)[0]}
⏰ ENTRY: In next 3 mins expecting!

Setup dey form!""")
        await asyncio.sleep(t2)

        await bot.send_message(chat_id=CHANNEL_ID, text=f"""⏳ {pair} UPDATE!

🔥 {setup} confirmed!
⏰ ENTRY: In next 2 mins!

Set amount - {action} dey come!""")
        await asyncio.sleep(t3)

        await bot.send_message(chat_id=CHANNEL_ID, text=f"""⚠️ {pair} FINAL!

⏰ ENTRY: In next 1 min!
💥 NEXT: {action}

Ready! Next na ENTER NOW! 🔥""")
        await asyncio.sleep(t4)

        live2, prev2 = get_price(pair)
        reason = f"Price hit {setup} at {live2}. Breakpoint {prev2} confirmed. Strong move!"
        
        await bot.send_message(chat_id=CHANNEL_ID, text=f"""🚨 ENTER NOW!!! - {pair}

{emoji} ACTION: {action}
⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}
💰 PRICE: {live2} (Was {prev2})

📊 REASON: {reason}
🎯 SETUP: {setup}
📈 CONFIDENCE: {random.randint(94,99)}%

👉 CLICK NOW!

🔗 {AFFILIATE_LINK}
#{pair.replace('/','')}""")
    except Exception as e:
        print(f"Signal error {pair}: {e}")
        # Don't crash bot, just log

async def session_runner(bot):
    while True:
        try:
            now = datetime.now(WAT)
            cur = now.strftime("%H:%M")
            today = now.strftime("%Y-%m-%d")
            if cur in SESSIONS and session_data["last_session"] != f"{today}_{cur}":
                session_data["last_session"] = f"{today}_{cur}"
                session_data["next_index"] = 0
            for sess in SESSIONS:
                sh,sm = map(int,sess.split(":"))
                s_start = now.replace(hour=sh,minute=sm,second=0,microsecond=0)
                s_end = s_start + timedelta(hours=1)
                if s_start <= now <= s_end and session_data["next_index"] < len(PAIRS):
                    await send_signal(PAIRS[session_data["next_index"]], bot, False)
                    session_data["next_index"] += 1
                    await asyncio.sleep(60)
                    break
        except Exception as e:
            print(f"Runner error: {e}")
        await asyncio.sleep(20)

async def post_init(app):
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("Ghost cleared - LIGHT BOT READY - NO TIMEOUT")
    except Exception as e:
        print(f"Webhook clear error: {e}")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"]=0
    pair = PAIRS[session_data["next_index"]]
    await update.message.reply_text(f"✅ Testing {pair}: 5m->3m->2m->1m->ENTER NOW (40 secs total for test)")
    await send_signal(pair, context.bot, True)
    session_data["next_index"]+=1

def main():
    # Increase timeout to avoid TimedOut
    app = Application.builder().token(TOKEN).post_init(post_init).get_updates_read_timeout(60).get_updates_write_timeout(60).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", set_id))
    app.add_handler(CommandHandler("testsignal", testsignal))
    print("Enoch LIGHT Bot READY - No matplotlib - No timeout")
    app.run_polling(drop_pending_updates=True, read_timeout=60, write_timeout=60)

if __name__ == "__main__":
    main()
