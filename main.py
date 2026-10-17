import os
import datetime
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
_raw_channel = os.environ.get("CHANNEL_ID", "@EnochStrategyBot")
# Convert -100... to int if possible
try:
    CHANNEL_ID = int(_raw_channel) if _raw_channel.lstrip('-').isdigit() else _raw_channel
except:
    CHANNEL_ID = _raw_channel

print(f"Starting with CHANNEL_ID: {CHANNEL_ID} type: {type(CHANNEL_ID)}", flush=True)

# FAKE SERVER FOR RENDER
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Enoch 3-Session Bot Live!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    print(f"Fake server on {port}", flush=True)
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- MESSAGES ---
async def warn_morning(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "⏰ MORNING SESSION in 10 mins!\n🕘 10:00AM WAT - GET READY!\n📊 EURUSD Loading...\n@EnochStrategyBot")
    except Exception as e:
        print(f"warn_morning error: {e}", flush=True)

async def signal_morning(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "📊 EURUSD MORNING - 10AM LIVE!\n🚀 London Open Started!\n🟢 BIAS: Breakout\nSL:15 | TP:30\nThis is not gambling, this is strategy!\n@EnochStrategyBot")
    except Exception as e:
        print(f"signal_morning error: {e}", flush=True)

async def warn_afternoon(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "⏰ AFTERNOON SESSION in 10 mins!\n🕑 2:00PM WAT - GET READY!\n📊 EURUSD Overlap\n@EnochStrategyBot")
    except Exception as e:
        print(f"warn_afternoon error: {e}", flush=True)

async def signal_afternoon(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "📊 EURUSD AFTERNOON - 2PM LIVE!\n🔥 London/NY Overlap Started!\n🟢 BIAS: Continuation\nSL:15 | TP:30\n@EnochStrategyBot")
    except Exception as e:
        print(f"signal_afternoon error: {e}", flush=True)

async def warn_evening(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "⏰ EVENING SESSION in 10 mins!\n🕖 7:00PM WAT - GET READY!\n📊 EURUSD NY Close\n@EnochStrategyBot")
    except Exception as e:
        print(f"warn_evening error: {e}", flush=True)

async def signal_evening(c):
    try:
        await c.bot.send_message(CHANNEL_ID, "📊 EURUSD EVENING - 7PM LIVE!\n🌙 NY Evening Started!\n🟢 BIAS: Reversal/Range\nSL:15 | TP:30\n@EnochStrategyBot")
    except Exception as e:
        print(f"signal_evening error: {e}", flush=True)

# COMMANDS
async def start(u,c): 
    await u.message.reply_text("✅ Bot LIVE! 3 Sessions:\n9:50/10AM Morning\n1:50/2PM Afternoon\n6:50/7PM Evening")

async def sig(u,c): 
    await signal_morning(c)
    await u.message.reply_text(f"Posted to {CHANNEL_ID}!")

def main():
    if not TOKEN:
        print("ERROR: BOT_TOKEN missing!", flush=True)
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", sig))
    
    jq = app.job_queue
    if jq is None:
        print("ERROR: job_queue is None! Install python-telegram-bot[job-queue]", flush=True)
        # Still run without jobs so /signal works
    else:
        # Morning WAT = UTC-1 => 10AM WAT = 9AM UTC
        jq.run_daily(warn_morning, time=datetime.time(8,50))
        jq.run_daily(signal_morning, time=datetime.time(9,0))
        jq.run_daily(warn_afternoon, time=datetime.time(12,50))
        jq.run_daily(signal_afternoon, time=datetime.time(13,0))
        jq.run_daily(warn_evening, time=datetime.time(17,50))
        jq.run_daily(signal_evening, time=datetime.time(18,0))
        print("Jobs scheduled", flush=True)
    
    print(f"BOT LIVE - 3 SESSIONS to {CHANNEL_ID}", flush=True)
    app.run_polling()

if __name__ == "__main__": 
    main()
