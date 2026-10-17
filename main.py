import os
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# YOUR TOKEN - NO NEED CHANGE
TOKEN = os.getenv("BOT_TOKEN", "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ")
LAGOS = ZoneInfo("Africa/Lagos")
CHANNEL = "@EnochStrategyBot"

# YOUR 3 SESSIONS
SESSIONS = [
    {"name": "MORNING", "start": "10:00", "end": "11:00"},
    {"name": "AFTERNOON", "start": "13:00", "end": "14:00"},
    {"name": "EVENING", "start": "17:00", "end": "20:00"},
]
PAIRS = ["EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "EUR/GBP OTC"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save user
    context.application.bot_data["users"].add(update.effective_user.id)
    await update.message.reply_text(
        "🛡️ THIS IS NOT GAMBLING\nTHIS IS STRATEGY\n\n"
        "✅ BOT LIVE & READY!\n\n"
        "3 Sessions Daily (WAT):\n"
        "🌅 MORNING 10-11\n"
        "☀️ AFTERNOON 13-14\n"
        "🌙 EVENING 17-20\n\n"
        "You go get signals for here and channel @EnochStrategyBot\n"
        "Evening session dey start soon!"
    )

async def signal_job(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(LAGOS)
    # Check if we dey inside session
    active = None
    for s in SESSIONS:
        sh, sm = map(int, s["start"].split(":"))
        eh, em = map(int, s["end"].split(":"))
        start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end = now.replace(hour=eh, minute=em, second=0, microsecond=0)
        if start <= now <= end:
            active = s
            break
    
    if not active:
        return

    # Generate signal
    pair = random.choice(PAIRS)
    direction = random.choice(["🟢 UP ⬆️", "🔴 DOWN ⬇️"])
    entry_time = (now + timedelta(minutes=2)).strftime("%H:%M")
    cur = now.strftime("%H:%M")

    text = (
        f"❗ ({cur} WAT) - {active['name']} SESSION\n"
        f"📊 {pair}\n"
        f"⏰ ENTRY: {entry_time}\n"
        f"Direction: {direction}\n\n"
        f"🛡️ STRATEGY > GAMBLING"
    )

    # Send to channel
    try:
        await context.bot.send_message(chat_id=CHANNEL, text=text)
        print(f"Sent to channel: {text}")
    except Exception as e:
        print(f"Channel error: {e}")

    # Send to all users wey press /start
    for uid in list(context.application.bot_data["users"]):
        try:
            await context.bot.send_message(chat_id=uid, text=text)
        except:
            pass

async def post_init(app: Application):
    app.bot_data["users"] = set()
    # Run every 5 minutes during session
    app.job_queue.run_repeating(signal_job, interval=300, first=10)
    print("BOT LIVE OK - JOB STARTED")

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    print("Starting polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
