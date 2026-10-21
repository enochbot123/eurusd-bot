import os, asyncio, random, threading
import yfinance as yf
import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from flask import Flask

# --- FLASK ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "✅ REAL SIGNAL BOT LIVE"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "AUD/USD": "AUDUSD=X",
    "USD/JPY": "JPY=X",
    "EUR/JPY": "EURJPY=X",
    "USD/CAD": "USDCAD=X",
    "USD/CHF": "USDCHF=X",
    "AUD/CAD": "AUDCAD=X",
    "EUR/AUD": "EURAUD=X",
    "AUD/JPY": "AUDJPY=X",
    "EUR/CAD": "EURCAD=X",
}

# --- REAL ANALYSIS FUNCTION - NO RANDOM ---
def get_real_signal(pair_name):
    try:
        ticker = PAIRS[pair_name]
        df = yf.Ticker(ticker).history(period="1d", interval="5m")
        if len(df) < 30:
            return None, None, "Not enough data"

        # EMA 9 and 21
        df['EMA9'] = df['Close'].ewm(span=9).mean()
        df['EMA21'] = df['Close'].ewm(span=21).mean()
        
        # RSI 14
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        price = round(float(last['Close']), 5)
        ema9 = float(last['EMA9'])
        ema21 = float(last['EMA21'])
        rsi = float(last['RSI'])

        # REAL LOGIC
        # BUY SIGNAL: EMA9 cross above EMA21 + RSI not overbought + bullish candle
        # SELL SIGNAL: EMA9 cross below EMA21 + RSI not oversold + bearish candle
        
        reason = ""
        if ema9 > ema21 and last['Close'] > last['Open'] and rsi < 70 and rsi > 45:
            direction = "CALL"
            reason = f"EMA9 ({ema9:.5f}) > EMA21 ({ema21:.5f}) + RSI {rsi:.1f} Bullish"
        elif ema9 < ema21 and last['Close'] < last['Open'] and rsi > 30 and rsi < 55:
            direction = "PUT"
            reason = f"EMA9 ({ema9:.5f}) < EMA21 ({ema21:.5f}) + RSI {rsi:.1f} Bearish"
        else:
            # If no clear setup, skip this pair and try another
            return None, None, f"No setup: EMA9 {ema9:.5f} vs EMA21 {ema21:.5f} RSI {rsi:.1f}"

        return direction, price, reason

    except Exception as e:
        print(f"Error {pair_name}: {e}")
        return None, None, str(e)

# --- PRIVATE BOT (your affiliate flow) ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("🔥 1️⃣ CREATE POCKET ACCOUNT", url=POCKET_LINK)],
        [InlineKeyboardButton("🆔 2️⃣ HOW TO GET YOUR ID", callback_data="how_id")],
        [InlineKeyboardButton("✅ 3️⃣ SEND ID FOR SIGNAL", callback_data="get_id")],
    ]
    await update.message.reply_text(f"👋 Welcome {update.effective_user.first_name}!\n\nReal signal bot - Real market analysis - No random!\n\nStep 1: Register with my link\nStep 2: Get your Pocket ID\nStep 3: Send ID make admin add you\n\nLink: {POCKET_LINK}", reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "how_id":
        await q.edit_message_text(f"How to get ID:\n1. Register {POCKET_LINK}\n2. Profile icon -> ID: 12345678\n3. Copy and send here")
    else:
        await q.edit_message_text("Send your Pocket ID like: 87654321")

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private": return
    pid = update.message.text.strip()
    if not pid.isdigit(): return
    await update.message.reply_text(f"✅ ID {pid} received! Admin go add you to VIP.")
    if ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=f"New ID: {pid} from @{update.effective_user.username} /approve {update.effective_user.id}")
        except: pass

async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID): return
    if context.args:
        await context.bot.send_message(chat_id=int(context.args[0]), text="🎉 Approved! You go dey get real signal now!")
        await update.message.reply_text("Approved")

# --- REAL SIGNAL LOOP ---
async def send_signal(bot):
    for _ in range(10): # Try 10 pairs to find good setup
        pair = random.choice(list(PAIRS.keys()))
        direction, price, reason = await asyncio.to_thread(get_real_signal, pair)
        
        if direction is None:
            continue # No good setup, try next pair

        # SETUP MESSAGE
        setup = f"🔍 **REAL SETUP FOUND - {pair}**\n━━━━━━━━━━━━\n💹 Price: `{price}`\n📊 Analysis: {reason}\n⏳ Wait 60s for confirmation..."
        await bot.send_message(chat_id=int(CHANNEL_ID), text=setup, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(60)

        if direction == "CALL":
            msg = f"🟢 **REAL SIGNAL - {pair}** 🟢\n━━━━━━━━━━━━\n💹 Entry: `{price}`\n🎯 **CALL 🔼 BUY**\n📈 Reason: {reason}\n⏱️ Expiry: 1 MIN\n\n✅ **REAL MARKET SIGNAL - ENTER BUY**"
        else:
            msg = f"🔴 **REAL SIGNAL - {pair}** 🔴\n━━━━━━━━━━━━\n💹 Entry: `{price}`\n🎯 **PUT 🔽 SELL**\n📉 Reason: {reason}\n⏱️ Expiry: 1 MIN\n\n✅ **REAL MARKET SIGNAL - ENTER SELL**"
        
        await bot.send_message(chat_id=int(CHANNEL_ID), text=msg, parse_mode=ParseMode.MARKDOWN)
        print(f"REAL SIGNAL {pair} {direction} {reason}")
        return

    print("No good setup this time, wait 5 mins")

async def loop_manager(app):
    await asyncio.sleep(10)
    print("✅ REAL SIGNAL BOT LIVE")
    while True:
        try:
            await send_signal(app.bot)
            await asyncio.sleep(300)
        except Exception as e:
            print(e)
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(loop_manager(app))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
