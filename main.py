import os
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@EnochStrategyBot")

# FAKE SERVER FOR RENDER
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Enoch 3-Session Bot Live!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- MESSAGES ---

async def warn_morning(c):
    await c.bot.send_message(CHANNEL_ID, "⏰ MORNING SESSION in 10 mins!\n🕘 10:00AM WAT - GET READY!\n📊 EURUSD Loading...\n@EnochStrategyBot")

async def signal_morning(c):
    await c.bot.send_message(CHANNEL_ID, "📊 EURUSD MORNING - 10AM LIVE!\n🚀 London Open Started!\n🟢 BIAS: Breakout\nSL:15 | TP:30\nThis is not gambling, this is strategy!\n@EnochStrategyBot")

async def warn_afternoon(c):
    await c.bot.send_message(CHANNEL_ID, "⏰ AFTERNOON SESSION in 10 mins!\n🕑 2:00PM WAT - GET READY!\n📊 EURUSD Overlap\n@EnochStrategyBot")

async def signal_afternoon(c):
    await c.bot.send_message(CHANNEL_ID, "📊 EURUSD AFTERNOON - 2PM LIVE!\n🔥 London/NY Overlap Started!\n🟢 BIAS: Continuation\nSL:15 | TP:30\n@EnochStrategyBot")

async def warn_evening(c):
    await c.bot.send_message(CHANNEL_ID, "⏰ EVENING SESSION in 10 mins!\n🕖 7:00PM WAT - GET READY!\n📊 EURUSD NY Close\n@EnochStrategyBot")

async def signal_evening(c):
    await c.bot.send_message(CHANNEL_ID, "📊 EURUSD EVENING - 7PM LIVE!\n🌙 NY Evening Started!\n🟢 BIAS: Reversal/Range\nSL:15 | TP:30\n@EnochStrategyBot")

# COMMANDS
async def start(u,c): await u.message.reply_text("✅ Bot LIVE! 3 Sessions:\n9:50/10AM Morning\n1:50/2PM Afternoon\n6:50/7PM Evening")
async def sig(u,c): await signal_morning(c); await u.message.reply_text("Posted!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", sig))
    
    jq = app.job_queue
    # Morning
    jq.run_daily(warn_morning, time=datetime.time(8,50))
    jq.run_daily(signal_morning, time=datetime.time(9,0))
    # Afternoon
    jq.run_daily(warn_afternoon, time=datetime.time(12,50))
    jq.run_daily(signal_afternoon, time=datetime.time(13,0))
    # Evening
    jq.run_daily(warn_evening, time=datetime.time(17,50))
    jq.run_daily(signal_evening, time=datetime.time(18,0))
    
    print(f"BOT LIVE - 3 SESSIONS to {CHANNEL_ID}")
    app.run_polling()

if __name__ == "__main__": main()
