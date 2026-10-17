import os
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
import datetime

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@EnochStrategyBot")

async def send_warning(context: ContextTypes.DEFAULT_TYPE):
    msg = """⏰ MORNING SESSION ALERT!
  
Morning session will start in 10 minutes - GET READY!

🕘 10:00AM WAT
📊 EURUSD Loading...
⚡️ Enoch Strategy

Stay tuned! @EnochStrategyBot"""
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        print("9:50 Warning sent")
    except Exception as e:
        print(f"Error: {e}")

async def send_morning_signal(context: ContextTypes.DEFAULT_TYPE):
    msg = """📊 EURUSD MORNING SESSION - 10AM LIVE!
🚀 Enoch Strategy STARTED!

THIS IS NOT GAMBLING, THIS IS STRATEGY!

🟢 BIAS: Waiting for London Open
💡 Strategy: 10AM - 12PM Breakout
SL: 15 pips | TP: 30 pips

@EnochStrategyBot"""
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        print(f"10AM Signal sent to {CHANNEL_ID}")
    except Exception as e:
        print(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot LIVE! ✅\n9:50AM Warning + 10AM Signal set daily!\nUse /signal to test")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_morning_signal(context)
    await update.message.reply_text("✅ Manual signal posted!")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("eurusd", signal))

    job_queue = app.job_queue
    # 9:50AM WAT = 8:50AM UTC
    job_queue.run_daily(send_warning, time=datetime.time(hour=8, minute=50, second=0))
    # 10:00AM WAT = 9:00AM UTC
    job_queue.run_daily(send_morning_signal, time=datetime.time(hour=9, minute=0, second=0))
    
    print(f"BOT LIVE - 9:50 + 10AM WAT to {CHANNEL_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
