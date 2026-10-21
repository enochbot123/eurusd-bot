import os
import asyncio
import random
import threading
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from flask import Flask

flask_app = Flask(__name__)
@flask_app.route('/')
def home():
    return "✅ Enoch Bot LIVE - UptimeRobot should see UP"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

LAGOS = pytz.timezone("Africa/Lagos")
SESSIONS = [
    {"start": "09:30", "end": "11:30"},
    {"start": "14:30", "end": "16:30"},
    {"start": "20:30", "end": "22:30"},
]
PAIRS = ["EUR/USD","AUD/USD","USD/JPY","EUR/JPY","USD/CAD","USD/CHF","AUD/CAD","EUR/AUD","AUD/JPY","EUR/CAD"]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔥 **ENOCH SIGNALS** 🔥\n\nRegister here 👉 {POCKET_LINK}\n\n💰 Type /risk 10\n⏰ 09:30-11:30, 14:30-16:30, 20:30-22:30 WAT", parse_mode=ParseMode.MARKDOWN)

async def risk_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("💰 Use: /risk 10 or /risk 50", parse_mode=ParseMode.MARKDOWN)
            return
        b = float(context.args[0])
        await update.message.reply_text(f"💰 **${b} Account**\n\n✅ 5%: ${round(b*0.05,2)}\n🛡️ 3%: ${round(b*0.03,2)}\n🎯 Target: ${round(b*0.2,2)}\n🛑 Stop: ${round(b*0.15,2)}\n\n{POCKET_LINK}", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Use: /risk 10")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot LIVE - Flask Active")

async def test_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Sending...")
    await send_professional_signal(context.bot)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower().strip() in ["start","hi","hello","help","link","menu"]:
        await start_cmd(update, context)

async def send_professional_signal(bot):
    try:
        payout=random.randint(82,96)
        pair=random.choice(PAIRS)
        direction=random.choice(["CALL 🔼","PUT 🔽"])
        m1=await bot.send_message(chat_id=CHANNEL_ID, text=f"🔔 **{pair} SETUP**\n💰 {payout}% - Wait 60s...", parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(60)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"🚀 **ENTER NOW {pair}**\n💥 {direction}\n💰 {payout}% - 1 MIN", parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(180)
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=m1.message_id)
        except:
            pass
    except Exception as e:
        print(e)

async def session_manager(app):
    await asyncio.sleep(10)
    print("✅ Bot with Website Ready")
    while True:
        try:
            cur=datetime.now(LAGOS).strftime("%H:%M")
            active=any(s["start"] <= cur <= s["end"] for s in SESSIONS)
            if active:
                await send_professional_signal(app.bot)
                await asyncio.sleep(random.randint(240,360))
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(e)
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(session_manager(app))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("testsignal", test_signal))
    app.add_handler(CommandHandler("risk", risk_cmd))
    app.add_handler(CommandHandler("calc", risk_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Starting with Flask on port...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
