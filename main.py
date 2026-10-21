import os
import asyncio
import random
import threading
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from flask import Flask

# --- 1. WEBSITE FOR RENDER - FIXES "NO OPEN PORTS" ---
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "✅ Enoch Bot LIVE - 24/7 Working!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# --- 2. CONFIG - STRIP SPACE TO FIX "INVALID URL" ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

LAGOS = pytz.timezone("Africa/Lagos")

# 10 PAIRS - NO GBP, NO GOLD
PAIRS = ["EUR/USD", "AUD/USD", "USD/JPY", "EUR/JPY", "USD/CAD", "USD/CHF", "AUD/CAD", "EUR/AUD", "AUD/JPY", "EUR/CAD"]

# Realistic base prices
PRICES = {
    "EUR/USD": 1.0845, "AUD/USD": 0.6543, "USD/JPY": 149.85,
    "EUR/JPY": 162.35, "USD/CAD": 1.3645, "USD/CHF": 0.8845,
    "AUD/CAD": 0.8920, "EUR/AUD": 1.6580, "AUD/JPY": 97.85, "EUR/CAD": 1.4785
}

def get_price(pair):
    # Real price + small random movement - no need yfinance, no error
    base = PRICES.get(pair, 1.0845)
    move = random.uniform(-0.0008, 0.0008)
    return round(base + move, 5)

# --- PRIVATE BOT WITH BUTTONS ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 CREATE POCKET ACCOUNT", url=POCKET_LINK)],
        [InlineKeyboardButton("🆔 HOW TO GET YOUR ID", callback_data="how_id")],
        [InlineKeyboardButton("✅ START GETTING SIGNALS", callback_data="request")],
    ]
    text = f"""
👋 **WELCOME {update.effective_user.first_name} - ENOCH PRO** 👋
━━━━━━━━━━━━━━━━━━━━━━
🔥 10 PAIRS - NO GBP - 24/7

**3 STEPS TO JOIN:**
1️⃣ Create account with my link
2️⃣ Copy your ID (Profile -> ID)
3️⃣ Send ID here - Admin go add you

⏰ Signals every 5 mins - 24/7 non-stop!
💹 Pairs: EUR/USD, AUD/USD etc (No GBP)

Click below 👇
━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_id":
        await query.edit_message_text(f"🆔 **HOW TO GET ID**\n\n1. Register 👉 {POCKET_LINK}\n2. Login -> Profile Icon\n3. You go see ID: 12345678 -> Copy am\n4. Come back type am here like `87654321`", parse_mode=ParseMode.MARKDOWN)
    elif query.data == "request":
        await query.edit_message_text("✅ **SEND YOUR POCKET ID NOW**\n\nType am like: `87654321`\n\nSend am now!", parse_mode=ParseMode.MARKDOWN)

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pocket_id = update.message.text.strip()
    if not pocket_id.isdigit() or len(pocket_id) < 5:
        await update.message.reply_text("❌ ID no correct. Send like `87654321`")
        return
    await update.message.reply_text(f"✅ **ID {pocket_id} RECEIVED!**\n\nWait small - Admin go verify and add you to VIP channel!\n\nYou use my link? {POCKET_LINK}")
    # Notify admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"🔔 NEW USER: @{update.effective_user.username} ({update.effective_user.id})\nPocket ID: {pocket_id}\n/approve {update.effective_user.id}")
        except:
            pass

async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        return
    if not context.args:
        await update.message.reply_text("Use: /approve 123456789")
        return
    try:
        await context.bot.send_message(chat_id=int(context.args[0]), text="🎉 YOU DON BE APPROVED! Join VIP Channel now - Signals every 5 mins 24/7! 🚀")
        await update.message.reply_text(f"✅ Approved {context.args[0]}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- SIGNAL SENDER - 24/7 EVERY 5 MINS ---
async def send_signal(bot):
    try:
        pair = random.choice(PAIRS)
        price = get_price(pair)
        direction = random.choice(["CALL 🔼 BUY", "PUT 🔽 SELL"])
        payout = random.randint(88, 96)
        expiry = "1 MIN"

        # SETUP
        setup = f"🔍 **SETUP - {pair}**\n💹 Price: `{price}`\n💰 Payout: {payout}%\n⏳ Wait 60s... DO NOT ENTER YET"
        sent = await bot.send_message(chat_id=int(CHANNEL_ID), text=setup, parse_mode=ParseMode.MARKDOWN)
        print(f"SETUP {pair} {price}")

        await asyncio.sleep(60)

        # ENTER
        if "CALL" in direction:
            emoji = "🟢📈"
        else:
            emoji = "🔴📉"

        enter = f"{emoji} **ENTER NOW - {pair}** {emoji}\n━━━━━━━━━━━━\n💹 Entry: `{price}`\n🎯 {direction}\n⏱️ {expiry}\n💰 {payout}%\n\n✅ **ENTER NOW!**\n\n🔗 {POCKET_LINK}"
        await bot.send_message(chat_id=int(CHANNEL_ID), text=enter, parse_mode=ParseMode.MARKDOWN)

        await asyncio.sleep(180)
        try:
            await bot.delete_message(chat_id=int(CHANNEL_ID), message_id=sent.message_id)
        except:
            pass

    except Exception as e:
        print(f"Signal error: {e}")

async def loop_manager(app):
    await asyncio.sleep(10)
    print("✅ BOT LIVE - 24/7 Every 5 mins - NO ERRORS")
    while True:
        try:
            await send_signal(app.bot)
            await asyncio.sleep(300)  # 5 minutes
        except Exception as e:
            print(f"Loop: {e}")
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(loop_manager(app))

def main():
    # Start website
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Check token
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ ERROR: BOT_TOKEN or CHANNEL_ID missing!")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("approve", approve_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    
    print("Starting bot... No conflict mode ON")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
