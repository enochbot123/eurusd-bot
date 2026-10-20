import os, random
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REGISTER_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003714315133")
ADMIN_USERNAME = "@Enochsystem"
WAT = ZoneInfo("Africa/Lagos")

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "GOLD", "EUR/JPY", "GBP/JPY"]

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER WITH POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("🆔 My Trading ID", callback_data='my_id')],
    ])

WELCOME = """⭐ ENOCH PROFESSIONAL SYSTEM ⭐

Hello {name} 👋

📊 SETTINGS:
Sessions: 9:30AM | 2:30PM | 8:30PM WAT
Expiry: 3 MIN [M3] | Entry M1
Strategy: Breakout + Retest

Channel: @EnochSignals
Support: {admin}
"""

# --- PRIVATE BOT PART ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME.format(name=update.effective_user.first_name, admin=ADMIN_USERNAME), reply_markup=main_menu())

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader_id = update.message.text
    print(f"NEW ID: {update.effective_user.first_name} ({update.effective_user.id}) => {trader_id} | CHANNEL: {CHANNEL_ID}")
    await update.message.reply_text(f"✅ Received!\nTrader ID: {trader_id}\nForwarded to admin!\n\nJoin channel for signals!", reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text("🆔 Send your Trading ID here in DM\nExample: 7654321", reply_markup=main_menu())

# --- CHANNEL AUTOMATIC TWO-STEP SIGNAL ---

async def set_pair_job(context: ContextTypes.DEFAULT_TYPE):
    pair = random.choice(PAIRS)
    text = f"""🔔 GET READY - SET YOUR PAIR!

💱 PAIR: {pair}
⚙️ SETUP: Breakout + Retest + Volume
📊 TIMEFRAME: M1
⏱️ EXPIRY: 3 MINUTES [M3]

⏳ WAIT FOR ENTRY SIGNAL IN 1 MINUTE...

🔗 {REGISTER_LINK}"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    print(f"SET PAIR: {pair} for {context.job.name}")
    # Schedule ENTER in 1 minute
    context.job_queue.run_once(enter_job, when=timedelta(minutes=1), data=pair, name=f"ENTER {pair}")

async def enter_job(context: ContextTypes.DEFAULT_TYPE):
    pair = context.job.data
    direction = random.choice(["BUY", "SELL"])
    dir_text = "BUY ⬆️ (CALL)" if direction == "BUY" else "SELL ⬇️ (PUT)"
    conf = random.randint(89, 96)
    text = f"""🚀 ENTER NOW!!! 🚀

💱 PAIR: {pair}
📈 DIRECTION: {dir_text}
⏱️ EXPIRY: 3 MINUTES [M3]
🧠 STRATEGY: Breakout + Volume Confirm
📊 CONFIDENCE: {conf}%

⚠️ RISK: 1% Only | Martingale 1 Step
👉 TAKE TRADE NOW ON M1!

🔗 TRADE NOW: {REGISTER_LINK}

Powered by Enoch System"""
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 TRADE NOW", url=REGISTER_LINK)]])
    await context.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=kb)
    print(f"ENTER: {pair} {direction}")

async def post_init(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)
    jq = app.job_queue
    for h,m in [(9,30),(14,30),(20,30)]: # WAT sessions
        jq.run_daily(set_pair_job, time=time(hour=h, minute=m, tzinfo=WAT), name=f"{h}:{m:02d} WAT")
    print(f"✅ Scheduler ready for {CHANNEL_ID} + Conflict fixed!")

def main():
    print("Bot started - Two-Step + Private Mode ON")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
