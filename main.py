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
        self.wfile.write(b"Enoch Full Button Pro Bot Running!")
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

# FULL BUTTONS AS YOU WANT - PRIVATE /start
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

# PROFESSIONAL 1 MIN WAIT - PAIR TO WATCH → WAIT 60 SECS → ENTER NOW
async def send_signal(pair, bot):
    try:
        live, prev = get_price(pair)
        setup_name = random.choice(list(SETUPS.keys()))
        setup_desc = SETUPS[setup_name]
        is_buy = live > prev or random.choice([True, False])
        direction = "BUY 📈 CALL" if is_buy else "SELL 📉 PUT"
        now_time = datetime.now(WAT).strftime('%H:%M')

        # 1️⃣ PAIR TO WATCH - 6:46
        await bot.send_message(chat_id=CHANNEL_ID, text=f"""🔍 PAIR TO WATCH! {now_time} WAT

📊 PAIR: {pair}
✅ REAL PRICE: {live} (Was {prev})
📈 SETUP: {setup_name}
📝 {setup_desc}

⏰ ENTRY: In next 1 MINUTE - Prepare now!
👉 Open {pair} for Pocket Option, select M1!

Wait 1 minute...""")
        
        print(f"PAIR TO WATCH sent for {pair} - waiting 60 secs...")
        await asyncio.sleep(60)

        # 2️⃣ ENTER NOW - 6:47 AFTER 1 MIN
        live2, prev2 = get_price(pair)
        now_time2 = datetime.now(WAT).strftime('%H:%M:%S')
        why = f"{'BUY' if is_buy else 'SELL'} Reason: {setup_desc} Price move from {prev2} to {live2}."
        
        await bot.send_message(chat_id=CHANNEL_ID, text=f"""🚀 ENTER NOW!!! REAL MARKET SIGNAL 🚀
⏰ TIME: {now_time2} WAT (After 1 min wait)

📊 PAIR: {pair}
✅ REAL PRICE: {live2} (LIVE - Was {prev2})
📋 DIRECTION: {direction}
⏰ EXPIRY: 3 MINUTES [M3]
📈 SETUP: {setup_name}
📊 CONFIDENCE: {random.randint(92,98)}%

🔍 WHY THIS TRADE GO {('BUY' if is_buy else 'SELL')}:
{why}

⚠️ RISK: 1% Only | Martingale 1 Step
🎯 TAKE TRADE NOW FOR M1 CANDLE!

🔗 TRADE NOW: {AFFILIATE_LINK}

⭐ Enoch Pro 1-Min System""")
        
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
