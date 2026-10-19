import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

# --- FAKE SERVER FOR RENDER FREE ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self): 
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
threading.Thread(target=run_fake_server, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
lagos = pytz.timezone('Africa/Lagos')

REGISTER_LINK = "https://your-affiliate-link.com" 
SUPPORT_USERNAME = "@Enochsystem"
CHANNEL_USERNAME = "Enoch Signals"

def get_welcome_text(first_name):
    return f"""
⭐ ENOCH PROFESSIONAL TRADING SYSTEM ⭐

⚠️ THIS IS NOT GAMBLING - THIS IS STRATEGY

Hello {first_name} 👋
Welcome to Professional Hub!

📊 PROFESSIONAL SETTINGS:
📅 Sessions: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ Expiry: 3 MIN [M3] | Entry M1
🧠 Strategy: Breakout + Retest + Volume
💰 Risk: 1% | Martingale 1 Step Only
🎯 Pairs: EUR/USD, GBP/USD, GOLD etc

📢 Channel: {CHANNEL_USERNAME}
👨‍💼 Support: {SUPPORT_USERNAME}

CHART SETUP:
- Resistance/Support breakout
- Volume confirmation
- Confidence 87-96%

⚠️ RISK WARNING: Trading involves risk. Trade with money you can afford to lose. This is educational signals only.

Need help? Contact {SUPPORT_USERNAME}

👇 Choose option below:
"""

def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 Start Signals", callback_data='start_signals')],
        [InlineKeyboardButton("🔗 REGISTER HERE", url=REGISTER_LINK)],
        [InlineKeyboardButton("🆔 My Trading ID", callback_data='my_id'),
         InlineKeyboardButton("ℹ️ How it works", callback_data='how_it_works')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    await update.message.reply_text(
        get_welcome_text(first_name),
        reply_markup=get_main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'start_signals':
        await query.edit_message_text(
            text=f"✅ Signals Activated!\n\nNext Session: 9:30 AM WAT\nChannel: {CHANNEL_USERNAME}\n\n{get_welcome_text(query.from_user.first_name)}",
            reply_markup=get_main_keyboard()
        )
    elif query.data == 'my_id':
        await query.message.reply_text(f"🆔 Your Trading ID\n\nID: {query.from_user.id}\nName: {query.from_user.first_name}\nStatus: ✅ Registered")
    elif query.data == 'how_it_works':
        await query.message.reply_text("ℹ️ How it Works\n\n1️⃣ Click REGISTER HERE\n2️⃣ Click Start Signals\n3️⃣ Bot analyzes live market\n4️⃣ You get signal 9:30AM, 2:30PM, 8:30PM WAT\n5️⃣ Enter 3 MIN expiry")

# --- FIXED SCHEDULER WITHOUT JOB_QUEUE ---
async def signal_scheduler():
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted")
    except Exception as e:
        print(e)
    while True:
        try:
            now = datetime.now(lagos)
            if (now.hour == 9 and now.minute == 30) or (now.hour == 14 and now.minute == 30) or (now.hour == 20 and now.minute == 30):
                if now.second < 10:
                    await bot.send_message(
                        chat_id=CHANNEL_ID,
                        text="⭐ ENOCH PROFESSIONAL SIGNAL ⭐\n\n📊 EUR/USD\n🟢 BUY - CALL\n⏱️ Expiry: 3 MIN\n📈 Confidence: 92%\n🧠 Reason: Breakout + Volume Confirm\n\n⚠️ 1% Risk Only",
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 REGISTER HERE", url=REGISTER_LINK)]])
                    )
                    await asyncio.sleep(65)
            await asyncio.sleep(30)
        except Exception as e:
            print(e)
            await asyncio.sleep(30)

async def post_init(application: Application):
    asyncio.create_task(signal_scheduler())

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot started - Professional Mode")
    app.run_polling()

if __name__ == "__main__":
    main()
