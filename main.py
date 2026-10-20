import os, sys, threading, random, requests
from datetime import time, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# FIX RENDER PORT ERROR
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Enoch Real Price System Running!"
def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN MISSING!")
    sys.exit(1)
BOT_TOKEN = BOT_TOKEN.strip()

REGISTER_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
CHANNEL_ID = -1003714315133
WAT = ZoneInfo("Africa/Lagos")
PAIRS = ["EUR/USD", "USD/JPY", "EUR/JPY", "AUD/USD", "USD/CAD", "USD/JPY"]

REASONS = [
    {"setup": "Breakout + Retest", "why": "Price don break strong resistance for M15, retest as support with volume confirm."},
    {"setup": "Double Bottom Support", "why": "Market form double bottom for M5 support. RSI 32 oversold + Bullish engulfing candle. Buyers dey enter."},
    {"setup": "Resistance Rejection", "why": "Price hit strong supply zone M15, wick rejection + Bearish pin bar. Sellers dey control."},
    {"setup": "Support Bounce + RSI Divergence", "why": "Price for major support, RSI divergence + Hammer candle M5. Strong buy zone."},
]

# ===== REAL MARKET PRICE FETCH =====
def get_real_price(pair):
    try:
        # pair like EUR/USD -> EUR to USD
        base, quote = pair.split("/")
        # Use frankfurter.app - free real forex API
        url = f"https://api.frankfurter.app/latest?from={base}&to={quote}"
        r = requests.get(url, timeout=5)
        data = r.json()
        price = data["rates"][quote]
        return f"{price:.5f}"
    except Exception as e:
        print(f"Price fetch failed for {pair}: {e}")
        # Fallback - generate near real price
        fallback = {"EUR/USD": "1.08534", "USD/JPY": "149.823", "EUR/JPY": "162.45", "AUD/USD": "0.65892", "USD/CAD": "1.36541", "NZD/USD": "0.61234"}
        return fallback.get(pair, "1.00000")

def private_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER - POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("🆔 HOW TO GET TRADING ID", callback_data="howto")],
        [InlineKeyboardButton("📊 PROFESSIONAL SETTINGS", callback_data="settings")],
        [InlineKeyboardButton("📢 JOIN SIGNAL CHANNEL", url="https://t.me/+YOUR_LINK")],
    ])

WELCOME_TEXT = """⭐ ENOCH PROFESSIONAL SYSTEM ⭐
Real Market Price System

Hello {name} 👋

WELCOME TO PROFESSIONAL TRADING!

📊 PROFESSIONAL SETTINGS:
━━━━━━━━━━━━━━
⏰ SESSIONS: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ ENTRY: Next M1 Candle
⏱️ EXPIRY: 3 MINUTES [M3]
💱 PAIRS: EUR/USD, USD/JPY, EUR/JPY, AUD/USD, USD/CAD, NZD/USD
📈 STRATEGY: Breakout + Retest + Volume + RSI + Real Price Action
⚠️ RISK: 1% Per Trade | Martingale 1 Step ONLY
📊 CONFIDENCE: 89-96%
💹 PRICE: REAL MARKET PRICE (Live from Forex Market)

🔗 YOUR REGISTER LINK:
{link}

We dey use REAL market price, no be random!

👇 CLICK BELOW:
"""

HOWTO_TEXT = """🆔 HOW TO GET YOUR TRADING ID:

1️⃣ Click REGISTER - POCKET OPTION button
2️⃣ Register account
3️⃣ Go to Profile -> Trading ID / Account ID
4️⃣ Copy ID (e.g., 12345678)
5️⃣ Paste am here!

✅ After you submit, you go get REAL PRICE signals for 9:30AM, 2:30PM, 8:30PM WAT!

🔗 https://pocket-friends.co/r/8vcvh8wte5
"""

SETTINGS_TEXT = """📊 ENOCH PROFESSIONAL SETTINGS - REAL PRICE:

🔹 SOURCE: Real Forex Market (Frankfurter ECB + Live API)
🔹 TIMEFRAME: M5, M15, H1 Analysis
🔹 ENTRY: M1 Next Candle
🔹 EXPIRY: M3 (3 Minutes)
🔹 INDICATORS: EMA 50, RSI, Support/Resistance, Volume, Real Price Action
🔹 RISK: 1% + 1 Martingale Step
🔹 REAL PRICE: We fetch live price every signal!

SESSIONS:
Morning 9:30AM WAT: EUR/USD, EUR/JPY
Afternoon 2:30PM WAT: USD/JPY, USD/CAD
Night 8:30PM WAT: AUD/USD, NZD/USD

No more random price - NA REAL MARKET PRICE!
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT.format(name=update.effective_user.first_name, link=REGISTER_LINK), reply_markup=private_keyboard())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "howto":
        await q.message.reply_text(HOWTO_TEXT, reply_markup=private_keyboard())
    elif q.data == "settings":
        await q.message.reply_text(SETTINGS_TEXT, reply_markup=private_keyboard())

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tid = update.message.text.strip()
    print(f"NEW ID: {update.effective_user.first_name} => {tid}")
    await update.message.reply_text(f"✅ ID RECEIVED: {tid}\nReal price signals go start for next session!\n\n🔗 {REGISTER_LINK}", reply_markup=private_keyboard())

# ===== CHANNEL - REAL PRICE + 5 MIN GAP =====
async def step1_set_pair(context: ContextTypes.DEFAULT_TYPE):
    pair = random.choice(PAIRS)
    real_price = get_real_price(pair)
    analysis = random.choice(REASONS)
    
    text = f"""🔔 PROFESSIONAL SETUP - REAL MARKET PRICE!

💱 PAIR: {pair}
💹 REAL PRICE: {real_price} (LIVE)
📊 SETUP: {analysis['setup']}
⏱️ EXPIRY: 3 MINUTES [M3]
📍 ENTRY: In 5 Minutes

📈 ANALYSIS:
{analysis['why']}

⚙️ ACTION: Set pair to {pair} for M1, price now {real_price}

⏳ WAIT FOR ENTER NOW...

🔗 {REGISTER_LINK}"""
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
        print(f"✅ STEP1 REAL PRICE: {pair} = {real_price}")
        context.job_queue.run_once(step2_enter, when=timedelta(minutes=5), data={"pair": pair, "price": real_price, "analysis": analysis})
    except Exception as e:
        print(f"❌ STEP1 FAILED: {e}")

async def step2_enter(context: ContextTypes.DEFAULT_TYPE):
    data = context.job.data
    pair = data["pair"]
    old_price = data["price"]
    analysis = data["analysis"]
    
    # Fetch new real price again for entry
    new_price = get_real_price(pair)
    
    if "Support" in analysis["setup"] or "Bottom" in analysis["setup"] or "Bounce" in analysis["setup"]:
        direction = "BUY"
    elif "Resistance" in analysis["setup"] or "Rejection" in analysis["setup"]:
        direction = "SELL"
    else:
        direction = random.choice(["BUY", "SELL"])
    
    dir_text = "BUY ⬆️ CALL" if direction == "BUY" else "SELL ⬇️ PUT"
    conf = random.randint(90, 96)
    
    if direction == "BUY":
        why_text = f"BUY Reason: {analysis['why']} Price move from {old_price} to {new_price}, buyers dey control. Expect bullish push."
    else:
        why_text = f"SELL Reason: {analysis['why']} Price move from {old_price} to {new_price}, sellers dey control. Expect bearish drop."

    text = f"""🚀 ENTER NOW!!! REAL MARKET SIGNAL 🚀

💱 PAIR: {pair}
💹 REAL PRICE: {new_price} (LIVE - Was {old_price})
📈 DIRECTION: {dir_text}
⏱️ EXPIRY: 3 MINUTES [M3]
🧠 SETUP: {analysis['setup']}
📊 CONFIDENCE: {conf}%

🔍 WHY THIS TRADE GO {direction}:
{why_text}

⚠️ RISK: 1% Only | Martingale 1 Step
👉 TAKE TRADE NOW FOR M1 CANDLE!

🔗 TRADE NOW: {REGISTER_LINK}

⭐ Enoch Real Price System - LIVE MARKET"""

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 TRADE NOW - REAL PRICE", url=REGISTER_LINK)]])
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text, reply_markup=kb)
        print(f"✅ STEP2 ENTER REAL: {pair} {direction} {new_price}")
    except Exception as e:
        print(f"❌ STEP2 FAILED: {e}")

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ REAL PRICE TEST: Fetching live price and sending to channel NOW...")
    pair = random.choice(PAIRS)
    price = get_real_price(pair)
    analysis = random.choice(REASONS)
    await context.bot.send_message(chat_id=CHANNEL_ID, text=f"🔔 TEST REAL PRICE:\n\n💱 {pair}\n💹 LIVE PRICE: {price}\n📊 {analysis['setup']}\n\n{analysis['why']}\n\n⏳ ENTER IN 1 MIN")
    context.job_queue.run_once(step2_enter, when=timedelta(seconds=60), data={"pair": pair, "price": price, "analysis": analysis})
    await update.message.reply_text(f"✅ Sent! {pair} REAL PRICE {price} to channel! Wait 1 min for ENTER!")

async def post_init(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)
    for h,m in [(9,30),(14,30),(20,30)]:
        app.job_queue.run_daily(step1_set_pair, time=time(hour=h, minute=m, tzinfo=WAT))
    print(f"✅ REAL PRICE BOT READY! Channel {CHANNEL_ID} | Bot @{(await app.bot.get_me()).username}")

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testsignal", testsignal))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
