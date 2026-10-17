import os
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@EnochStrategyBot")

# FAKE WEBSERVER TO SATISFY RENDER
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Enoch Bot is Live!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

async def send_warning(context: ContextTypes.DEFAULT_TYPE):
    msg = """⏰ MORNING SESSION ALERT!
  
Morning session will start in 10 minutes - GET READY!

🕘 10:00AM WAT
📊 EURUSD Loading...
⚡️ Enoch Strategy

Stay tuned! @EnochStrategyBot"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)

async def send_morning_signal(context: ContextTypes.DEFAULT_TYPE):
    msg = """📊 EURUSD MORNING SESSION - 10AM LIVE!
🚀 Enoch Strategy STARTED!

THIS IS NOT GAMBLING, THIS IS STRATEGY!

🟢 BIAS: London Open
💡 Strategy: 10AM - 12PM Breakout
SL: 15 | TP: 30
@EnochStrategyBot"""
    await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot LIVE! ✅\n9:50AM Warning + 10AM Signal daily!")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_morning_signal(context)
    await update.message.reply_text("✅ Posted!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("eurusd", signal))
    
    jq = app.job_queue
    jq.run_daily(send_warning, time=datetime.time(hour=8, minute=50, second=0))
    jq.run_daily(send_morning_signal, time=datetime.time(hour=9, minute=0, second=0))
    
    print(f"BOT LIVE - 9:50 + 10AM WAT to {CHANNEL_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
