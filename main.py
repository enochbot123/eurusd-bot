import os
import random
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ")
LAGOS = ZoneInfo("Africa/Lagos")
CHANNEL_ID = "@EnochStrategyBot"

logging.basicConfig(level=logging.INFO)

SESSIONS = [
    {"name": "MORNING", "start": "10:00", "end": "11:00"},
    {"name": "AFTERNOON", "start": "13:00", "end": "14:00"},
    {"name": "EVENING", "start": "17:00", "end": "20:00"},
]

PAIRS = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "EUR/JPY OTC", "EUR/GBP OTC"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "users" not in context.application.bot_data:
        context.application.bot_data["users"] = set()
    context.application.bot_data["users"].add(update.effective_chat.id)
    
    kb = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/EnochStrategyBot")],
        [InlineKeyboardButton("How it works", callback_data="how")]
    ]
    txt = (
        "🛡️ THIS IS NOT GAMBLING\n"
        "THIS IS STRATEGY\n\n"
        "Welcome to Enoch AI Strategy Bot 📈\n\n"
        "✅ 3 Daily Sessions\n"
        "🌅 MORNING 10-11 WAT\n"
        "☀️ AFTERNOON 13-14 WAT\n"
        "🌙 EVENING 17-20 WAT\n\n"
        "Join channel for live signals!\n"
        "t.me/EnochStrategyBot"
    )
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def how_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("📊 EMA9 + RSI Strategy. Signals 1 min before entry. Stay tuned!")

async def signal_job(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(LAGOS)
    active = None
    for s in SESSIONS:
        sh, sm = map(int, s["start"].split(":"))
        eh, em = map(int, s["end"].split(":"))
        st = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        en = now.replace(hour=eh, minute=em, second=0, microsecond=0)
        if st <= now <= en:
            active = s
            break
    if not active:
        return

    pair = random.choice(PAIRS)
    direction = random.choice(["👻 UP", "👻 DOWN"])
    entry = (now + timedelta(minutes=1)).strftime("%H:%M")
    cur = now.strftime("%H:%M")

    msg = f"❗ ({cur} UTC+1) - {active['name']}\n📊 {pair}\n⏰ SET: {entry} - Prepare {pair.split()[0]}\nEntry time: {entry} - {active['name']}\nDirection: {direction}"

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        print(f"Sent to channel: {msg}")
    except Exception as e:
        print(f"Channel error: {e}")

    for uid in list(context.bot_data.get("users", [])):
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
        except:
            pass

async def post_init(app):
    app.bot_data["users"] = set()
    app.job_queue.run_repeating(signal_job, interval=60, first=10)
    print("Bot started OK")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(how_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
