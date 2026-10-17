import os
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"

LAGOS = ZoneInfo("Africa/Lagos")
CHANNEL_ID = "@EnochStrategyBot"

SESSIONS = [
    {"name": "MORNING", "start": "10:00", "end": "11:00"},
    {"name": "AFTERNOON", "start": "13:00", "end": "14:00"},
    {"name": "EVENING", "start": "17:00", "end": "20:00"},
]
PAIRS = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.application.bot_data.setdefault("users", set()).add(update.effective_chat.id)
    kb = [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/EnochStrategyBot")]]
    txt = "🛡️ THIS IS NOT GAMBLING\nTHIS IS STRATEGY\n\nWelcome! I dey LIVE now ✅\n\n3 Sessions daily:\n🌅 10-11 WAT\n☀️ 13-14 WAT\n🌙 17-20 WAT\n\nJoin channel for signals!"
    await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb))

async def job(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(LAGOS)
    active = None
    for s in SESSIONS:
        sh, sm = map(int, s["start"].split(":"))
        eh, em = map(int, s["end"].split(":"))
        st = now.replace(hour=sh, minute=sm, second=0)
        en = now.replace(hour=eh, minute=em, second=0)
        if st <= now <= en:
            active = s
            break
    if not active:
        return
    pair = random.choice(PAIRS)
    direction = random.choice(["👻 UP", "👻 DOWN"])
    entry = (now + timedelta(minutes=1)).strftime("%H:%M")
    cur = now.strftime("%H:%M")
    msg = f"❗ ({cur} UTC+1) - {active['name']}\n📊 {pair}\n⏰ SET: {entry}\nEntry time: {entry} - {active['name']}\nDirection: {direction}"
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
    except Exception as e:
        print(f"Channel fail: {e}")
    for uid in list(context.bot_data.get("users", [])):
        try:
            await context.bot.send_message(chat_id=uid, text=msg)
        except:
            pass

async def post_init(app: Application):
    app.bot_data["users"] = set()
    app.job_queue.run_repeating(job, interval=60, first=10)
    print("BOT LIVE OK")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
