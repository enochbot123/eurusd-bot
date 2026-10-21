import os
import asyncio
import random
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# CLEAN ENV - comot dirty spaces
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

print(f"BOT_TOKEN loaded: {len(BOT_TOKEN)} chars")
print(f"CHANNEL_ID loaded: '{CHANNEL_ID}'")

LAGOS = pytz.timezone("Africa/Lagos")

SESSIONS = [
    {"name": "MORNING SESSION ☀️", "start": "09:30", "end": "11:30"},
    {"name": "AFTERNOON SESSION 🌤️", "start": "14:30", "end": "16:30"},
    {"name": "NIGHT SESSION 🌙", "start": "20:30", "end": "22:30"},
]

PAIRS = ["EUR/USD","AUD/USD","USD/JPY","EUR/JPY","USD/CAD","USD/CHF","AUD/CAD","EUR/AUD","AUD/JPY","EUR/CAD"]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
🔥 **ENOCH PROFESSIONAL SIGNALS** 🔥
━━━━━━━━━━━━━━━━━━━━━━
Welcome {update.effective_user.first_name}! 👋

**STEP 1️⃣ - REGISTER**
👉 {POCKET_LINK}

**STEP 2️⃣ - DEPOSIT**
Min $10 - Use Crypto

**STEP 3️⃣ - USE SIGNAL**
Wait for SETUP, then ENTER

**⏰ TIMES (Lagos):**
☀️ 09:30-11:30 | 🌤️ 14:30-16:30 | 🌙 20:30-22:30

**💰 Type /risk 10**

**Register 👇**
👉 {POCKET_LINK}
━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def risk_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("💰 Use: /risk 10 or /risk 50", parse_mode=ParseMode.MARKDOWN)
            return
        balance = float(context.args[0])
        safe = round(balance*0.05,2)
        safe3 = round(balance*0.03,2)
        target = round(safe*4,2)
        stop = round(balance*0.15,2)
        await update.message.reply_text(f"💰 **FOR ${balance}**\n\n✅ 5%: ${safe}\n🛡️ 3%: ${safe3}\n🎯 Target: ${target}\n🛑 Stop: ${stop}\n\n{POCKET_LINK}", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Use: /risk 10")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot LIVE", parse_mode=ParseMode.MARKDOWN)

async def test_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Sending test...")
    await send_professional_signal(context.bot)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text in ["start","hello","hi","help","menu","register","link"]:
        await start_cmd(update, context)
    elif "risk" in text:
        try:
            parts=text.split()
            if len(parts)>1:
                context.args=[parts[1]]
                await risk_cmd(update, context)
        except:
            pass

async def send_professional_signal(bot):
    try:
        payout=random.randint(82,96)
        pair=random.choice(PAIRS)
        direction=random.choice(["CALL 🔼","PUT 🔽"])
        msg1=f"🔔 **{pair} - SETUP LOADING**\n\n⏳ PAIR TO WATCH\n💰 {payout}%\n⚠️ Wait 60s..."
        sent1=await bot.send_message(chat_id=CHANNEL_ID, text=msg1, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(60)
        msg2=f"🚀 **ENTER NOW - {pair}**\n\n💥 {direction}\n💰 {payout}%\n⏱️ 1 MIN"
        await bot.send_message(chat_id=CHANNEL_ID, text=msg2, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(180)
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=sent1.message_id)
        except:
            pass
    except Exception as e:
        print(f"Signal error: {e}")

async def session_manager(app):
    await asyncio.sleep(10)
    print("✅ Bot Started Clean")
    while True:
        try:
            current=datetime.now(LAGOS).strftime("%H:%M")
            active=False
            for s in SESSIONS:
                if s["start"] <= current <= s["end"]:
                    active=True
                    break
            if active:
                await send_professional_signal(app.bot)
                await asyncio.sleep(random.randint(240,360))
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}")
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(session_manager(app))

def main():
    app=ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("testsignal", test_signal))
    app.add_handler(CommandHandler("risk", risk_cmd))
    app.add_handler(CommandHandler("calc", risk_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__=="__main__":
    main()
