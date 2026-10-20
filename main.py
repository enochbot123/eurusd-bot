import os, random
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REGISTER_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
CHANNEL_ID = "-1003714315133"
WAT = ZoneInfo("Africa/Lagos")

PAIRS = ["EUR/USD", "USD/JPY", "EUR/JPY", "AUD/USD", "USD/CAD"]

# === PRIVATE ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER", url=REGISTER_LINK)],
        [InlineKeyboardButton("📢 TEST SIGNAL NOW", callback_data="test")],
    ])
    await update.message.reply_text(f"⭐ ENOCH SYSTEM ⭐\nHello {update.effective_user.first_name}\nSessions: 9:30AM | 2:30PM | 8:30PM WAT\n\nType /testsignal to force signal for channel NOW!", reply_markup=kb)

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Received: {update.message.text}")

# === CHANNEL TWO-STEP ===
async def step1_set_pair(context: ContextTypes.DEFAULT_TYPE):
    pair = random.choice(PAIRS)
    text = f"🔔 GET READY - SET YOUR PAIR!\n\n💱 PAIR: {pair}\n⏱️ EXPIRY: 3 MIN [M3]\n\n⏳ ENTRY IN 1 MINUTE..."
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
        print(f"✅ STEP1 SENT: {pair} to {CHANNEL_ID}")
        context.job_queue.run_once(step2_enter, when=timedelta(minutes=1), data=pair, name=f"ENTER {pair}")
    except Exception as e:
        print(f"❌ STEP1 FAILED: {e} - CHECK IF BOT IS ADMIN IN CHANNEL {CHANNEL_ID}!")

async def step2_enter(context: ContextTypes.DEFAULT_TYPE):
    pair = context.job.data
    direction = random.choice(["BUY", "SELL"])
    d_text = "BUY ⬆️ CALL" if direction == "BUY" else "SELL ⬇️ PUT"
    conf = random.randint(90,96)
    text = f"🚀 ENTER NOW!!!\n\n💱 PAIR: {pair}\n📈 {d_text}\n⏱️ EXPIRY: 3 MIN [M3]\n📊 CONF: {conf}%\n\n🔗 {REGISTER_LINK}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 TRADE NOW", url=REGISTER_LINK)]])
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=kb)
    print(f"✅ STEP2 SENT: {pair} {direction}")

# === MANUAL TEST COMMAND ===
async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ FORCING SIGNAL NOW FOR CHANNEL...")
    await step1_set_pair(context)
    await update.message.reply_text("✅ Step 1 sent! Wait 1 minute for ENTER!")

async def post_init(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)
    jq = app.job_queue
    if not jq:
        print("❌ job_queue is None! Fix requirements.txt")
        return
    # Schedule 3 sessions WAT
    for h,m in [(9,30),(14,30),(20,30)]:
        jq.run_daily(step1_set_pair, time=time(hour=h, minute=m, tzinfo=WAT), name=f"{h}:{m:02d}")
    print(f"✅ SCHEDULER READY FOR {CHANNEL_ID} | Pairs: {PAIRS} | Next: 9:30, 14:30, 20:30 WAT")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testsignal", testsignal))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
