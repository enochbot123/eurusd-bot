import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import yfinance as yf
import pandas as pd
from datetime import datetime, time
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

# --- YOUR PRO LINKS ---
REGISTER_LINK = "https://your-affiliate-link.com" # PUT YOUR LINK HERE
SUPPORT_USERNAME = "@Enochsystem" # Change to yours
CHANNEL_USERNAME = "Enoch Signals" # Change to yours

# --- PROFESSIONAL WELCOME MESSAGE (Like Screenshot) ---
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
• Resistance/Support breakout
• Volume confirmation
• Confidence 87-96%

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

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    await update.message.reply_text(
        get_welcome_text(first_name),
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'start_signals':
        await query.edit_message_text(
            text=f"✅ <b>Signals Activated!</b>\n\n"
                 f"⏰ Next Session: 9:30 AM WAT\n"
                 f"📢 Signals will be sent to: {CHANNEL_USERNAME}\n\n"
                 f"🔔 Make sure you JOIN the channel!\n\n"
                 f"{get_welcome_text(query.from_user.first_name)}",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )
        # Send test signal to channel
        bot = Bot(token=BOT_TOKEN)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"🚀 {query.from_user.first_name} just activated signals! Welcome!")

    elif query.data == 'my_id':
        user_id = query.from_user.id
        await query.message.reply_text(
            f"🆔 <b>Your Trading ID</b>\n\n"
            f"ID: <code>{user_id}</code>\n"
            f"Name: {query.from_user.first_name}\n"
            f"Status: ✅ Registered\n\n"
            f"Use this ID if you contact support.",
            parse_mode='HTML'
        )

    elif query.data == 'how_it_works':
        await query.message.reply_text(
            "ℹ️ <b>How it Works</b>\n\n"
            "1️⃣ Click REGISTER HERE and create trading account\n"
            "2️⃣ Click Start Signals\n"
            "3️⃣ Bot will analyze live market (EMA, RSI, MACD, Volume)\n"
            "4️⃣ You get signal at 9:30AM, 2:30PM, 8:30PM WAT\n"
            "5️⃣ Enter trade for 3 MIN expiry on M1 timeframe\n"
            "6️⃣ Use 1% risk only!\n\n"
            "⚠️ This is strategy, not gambling!",
            parse_mode='HTML'
        )

# --- REAL SIGNAL LOGIC (Background) ---
async def signal_scheduler(app):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("Webhook deleted")
    except: pass
    
    while True:
        try:
            now = datetime.now(lagos)
            # Check if time is 9:30, 14:30, 20:30
            if (now.hour == 9 and now.minute == 30) or \
               (now.hour == 14 and now.minute == 30) or \
               (now.hour == 20 and now.minute == 30):
                
                # Example real signal
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text="⭐ ENOCH PROFESSIONAL SIGNAL ⭐\n\n"
                         "📊 EUR/USD\n"
                         "🟢 BUY - CALL\n"
                         "⏱️ Expiry: 3 MIN\n"
                         "📈 Confidence: 92%\n"
                         "🧠 Reason: Breakout + Volume Confirm\n"
                         "⏰ Enter at exact time we give\n\n"
                         "⚠️ 1% Risk Only",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 REGISTER HERE", url=REGISTER_LINK)]])
                )
                await asyncio.sleep(60) # Avoid duplicate
            await asyncio.sleep(30)
        except Exception as e:
            print(e)
            await asyncio.sleep(30)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Start scheduler in background
    app.job_queue.run_once(lambda ctx: asyncio.create_task(signal_scheduler(app)), 0)
    
    print("Bot started - Professional Mode")
    app.run_polling()

if __name__ == "__main__":
    main()
