import os
import asyncio
import random
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

# CLEAN ENV - comot dirty spaces wey cause InvalidURL
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

# 10 SHARP PAIRS - NO GBP/USD, NO GOLD
PAIRS = [
    "EUR/USD",
    "AUD/USD",
    "USD/JPY",
    "EUR/JPY",
    "USD/CAD",
    "USD/CHF",
    "AUD/CAD",
    "EUR/AUD",
    "AUD/JPY",
    "EUR/CAD"
]

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"""
🔥 **ENOCH PROFESSIONAL SIGNALS** 🔥
━━━━━━━━━━━━━━━━━━━━━━
Welcome {update.effective_user.first_name}! 👋

You wan make money with my sharp signals? Follow 3 steps 👇

**STEP 1️⃣ - REGISTER (Important!)**
You MUST register with my link to get signals working well:
👉 {POCKET_LINK}

⚠️ If you no use my link, signals fit no sync well!

**STEP 2️⃣ - DEPOSIT**
- Minimum na $10
- For Naija use Crypto (USDT) - fast!

**STEP 3️⃣ - HOW TO USE SIGNAL**
1. Bot go send: PAIR TO WATCH
2. Wait 60 seconds
3. Bot go send: ENTER NOW CALL/PUT
4. Enter immediately for 1 min expiry

━━━━━━━━━━━━━━━━━━━━━━
**⏰ SIGNAL TIMES (Lagos):**
☀️ 09:30-11:30 | 🌤️ 14:30-16:30 | 🌙 20:30-22:30

**🎯 10 SHARP PAIRS:**
EUR/USD, AUD/USD, USD/JPY + 7 more
❌ No GBP/USD, No Gold
✅ Only 82-96% Payout

**💰 RISK CALC:**
Type /risk 10 - e go show you how much to stake

**Click to Register Now 👇**
👉 {POCKET_LINK}
━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def risk_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("💰 **Use am like:**\n\n/risk 10 - for $10 account\n/risk 50 - for $50 account", parse_mode=ParseMode.MARKDOWN)
            return
        balance = float(context.args[0])
        safe_stake = round(balance * 0.05, 2)
        pro_stake = round(balance * 0.03, 2)
        daily_target = round(safe_stake * 4, 2)
        max_loss = round(balance * 0.15, 2)
        msg = f"""
💰 **RISK CALC FOR ${balance}**
━━━━━━━━━━━━━━━━━━━━━━
**Balance:** ${balance}

**✅ RECOMMENDED (5%):**
Stake: **${safe_stake}**
Daily Target: **${daily_target}**
Stop Loss: **${max_loss}**

**🛡️ SAFEST (3%):**
Stake: **${pro_stake}**

**Register here 👇**
{POCKET_LINK}
━━━━━━━━━━━━━━━━━━━━━━
"""
        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text("Use: /risk 10")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(LAGOS).strftime("%H:%M:%S")
    await update.message.reply_text(f"✅ **Bot LIVE**\n🕒 {now} WAT\n🔥 10 Sharp Pairs\n💰 Link: {POCKET_LINK}", parse_mode=ParseMode.MARKDOWN)

async def test_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧪 Sending test signal to channel...")
    await send_professional_signal(context.bot)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    if text in ["start", "hello", "hi", "help", "menu", "register", "link"]:
        await start_cmd(update, context)
    elif "risk" in text:
        try:
            parts = text.split()
            if len(parts) > 1:
                context.args = [parts[1]]
                await risk_cmd(update, context)
            else:
                await update.message.reply_text("Type: /risk 10")
        except:
            pass

async def send_professional_signal(bot):
    try:
        payout = random.randint(82, 96)
        pair = random.choice(PAIRS)
        direction = random.choice(["CALL 🔼", "PUT 🔽"])
        
        msg1 = f"""
🔔 **{pair} - SETUP LOADING**
━━━━━━━━━━━━━━━━
⏳ **ACTION:** PAIR TO WATCH
💰 **Payout:** {payout}%
⏱️ **Expiry:** 1 MIN
📊 **Confidence:** HIGH ⭐⭐⭐

⚠️ **DO NOT ENTER YET!**
Wait 60s...
━━━━━━━━━━━━━━━━
"""
        sent1 = await bot.send_message(chat_id=CHANNEL_ID, text=msg1, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(60)
        
        msg2 = f"""
🚀 **ENTER NOW - {pair}**
━━━━━━━━━━━━━━━━
💥 **DIRECTION:** {direction}
💰 **Payout:** {payout}%
⏱️ **Expiry:** 1 MIN
🎯 **Entry:** IMMEDIATELY!

✅ **SHARP SIGNAL**
━━━━━━━━━━━━━━━━
"""
        await bot.send_message(chat_id=CHANNEL_ID, text=msg2, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(180)
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=sent1.message_id)
        except:
            pass
    except Exception as e:
        print(f"Signal error: {e}")
        return

async def session_manager(app):
    await asyncio.sleep(10)
    print("✅ Bot Started Clean - No Conflict")
    while True:
        try:
            now = datetime.now(LAGOS)
            current_time = now.strftime("%H:%M")
            active = False
            for s in SESSIONS:
                if s["start"] <= current_time <= s["end"]:
                    active = True
                    break
            if active:
                await send_professional_signal(app.bot)
                await asyncio.sleep(random.randint(240, 360))
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}")
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(session_manager(app))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("testsignal", test_signal))
    app.add_handler(CommandHandler("risk", risk_cmd))
    app.add_handler(CommandHandler("calc", risk_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("Polling started...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
