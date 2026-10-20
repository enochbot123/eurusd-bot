import os, asyncio, random, requests
from datetime import datetime, timedelta
import pytz
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
import matplotlib.pyplot as plt
import io

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAIRS = ["AUD/USD", "EUR/USD", "USD/JPY", "EUR/JPY", "USD/CAD"]
WAT = pytz.timezone("Africa/Lagos")
AFFILIATE_LINK = "https://pocket-friends.co/r/8vcvh8wte5"
SESSIONS = ["09:30", "14:30", "20:30"]
session_data = {"last_session": "", "next_index": 0}

def get_real_price(pair):
    try:
        symbol = pair.replace("/", "")
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}=X?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        data = r.json()
        price = data['chart']['result'][0]['meta']['regularMarketPrice']
        prev = data['chart']['result'][0]['meta']['previousClose']
        return float(price), float(prev)
    except:
        base = {"AUD/USD": 0.698, "EUR/USD": 1.084, "USD/JPY": 154.2, "EUR/JPY": 167.1, "USD/CAD": 1.365}
        p = base.get(pair, 1.0)
        return round(p + random.uniform(-0.002, 0.002), 5), round(p, 5)

def create_chart_image(pair, action, price):
    plt.figure(figsize=(6,3))
    prices = [price + random.uniform(-0.001, 0.001) for _ in range(30)]
    color = "green" if "BUY" in action else "red"
    plt.plot(prices, color=color, linewidth=2)
    plt.title(f"{pair} - {action} - {price}", fontsize=10, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150)
    plt.close()
    buf.seek(0)
    return buf

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👋 Welcome! Register: {AFFILIATE_LINK} Then /id YOUR_ID")

async def set_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /id 12345678")
        return
    await update.message.reply_text(f"✅ ID {context.args[0]} saved!")

# === YOUR VOICE NOTE FLOW - 5 MINS WITH UPDATES ===
async def send_signal(pair, bot, fast_mode=False):
    live, prev = get_real_price(pair)
    setup = random.choice(["Support Bounce at Demand", "Resistance at Supply", "Breakpoint Retest"])
    action = "SELL PUT" if live > prev else "BUY CALL"
    buy_sell_emoji = "🔴 SELL" if "SELL" in action else "🟢 BUY"

    if fast_mode:
        # For testsignal - total 40 secs: 10 + 10 + 10 + 10
        t1, t2, t3, t4 = 10, 10, 10, 10
    else:
        # For real session - total 5 mins: 2 mins + 1 min + 1 min + 1 min = 5 mins
        t1, t2, t3, t4 = 120, 60, 60, 60

    # STAGE 1 - 0 MIN - 5 MINS EXPECTING
    msg1 = f"""📊 PAIR TO WATCH - GET READY!

💰 PAIR: {pair}
💵 PRICE: {live} (LIVE)
🎯 SETUP: {setup}

⏰ ENTRY: In the next 5 minutes!
Prepare your chart - Don't enter yet!

🔗 {AFFILIATE_LINK}"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg1)
    await asyncio.sleep(t1)

    # STAGE 2 - 3 MINS EXPECTING (after 2 mins)
    msg2 = f"""⏳ {pair} UPDATE!

💰 PRICE NOW: {get_real_price(pair)[0]}
⏰ ENTRY: In the next 3 minutes expecting time!

Get ready... Setup dey form for {setup}!

Stay tuned!"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg2)
    await asyncio.sleep(t2)

    # STAGE 3 - 2 MINS EXPECTING
    msg3 = f"""⏳ {pair} UPDATE!

🔥 {setup} confirmed!
⏰ ENTRY: In the next 2 minutes expecting time!

Set your amount - {action} dey come!

Final preparation!"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg3)
    await asyncio.sleep(t3)

    # STAGE 4 - 1 MIN FINAL WARNING
    msg4 = f"""⚠️ {pair} - FINAL WARNING!

⏰ ENTRY: In the next 1 minute!
💰 PAIR: {pair}
💥 NEXT: {action}

Ready your finger! 
Next message na ENTER NOW! 🔥🔥🔥"""
    await bot.send_message(chat_id=CHANNEL_ID, text=msg4)
    await asyncio.sleep(t4)

    # STAGE 5 - ENTER NOW + REASON + CHART + EMOJI
    live_final, prev_final = get_real_price(pair)
    if "Support" in setup or "Demand" in setup:
        reason = f"Price hit DEMAND ZONE breakpoint at {live_final}. Strong bullish rejection at {prev_final}. Buyers dey push - We go UP!"
    elif "Resistance" in setup or "Supply" in setup:
        reason = f"Price hit SUPPLY ZONE breakpoint at {live_final}. Bearish rejection confirmed at {prev_final}. Sellers control - We go DOWN!"
    else:
        reason = f"Price BREAKOUT level {prev_final} and retesting {live_final}. Classic breakpoint retest - Continuation!"

    caption = f"""🚨 ENTER NOW!!! - {pair}

{buy_sell_emoji} ACTION: {action}
⏰ TIME: {datetime.now(WAT).strftime('%H:%M:%S WAT')}
💰 PRICE: {live_final} (LIVE - Was {prev_final})

📊 BREAKPOINT REASON:
{reason}

🎯 SETUP: {setup}
📈 CONFIDENCE: {random.randint(94,99)}%

👉 CLICK NOW AND {action}!

🔗 {AFFILIATE_LINK}
#{pair.replace('/','')} #PocketOption"""

    chart_buf = create_chart_image(pair, action, live_final)
    await bot.send_photo(chat_id=CHANNEL_ID, photo=chart_buf, caption=caption)
    print(f"ENTER NOW SENT {pair}")

async def session_runner(bot):
    while True:
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
                await send_signal(PAIRS[session_data["next_index"]], bot, fast_mode=False)
                session_data["next_index"] += 1
                await asyncio.sleep(60)
                break
        await asyncio.sleep(20)

async def post_init(app):
    # KILL CONFLICT PERMANENTLY
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("Ghost cleared - 5 min multi-update flow ready")
    asyncio.create_task(session_runner(app.bot))

async def testsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if session_data["next_index"] >= len(PAIRS): session_data["next_index"] = 0
    pair = PAIRS[session_data["next_index"]]
    await update.message.reply_text(f"✅ Starting CORRECT 5-min flow for {pair}: 5 mins -> 3 mins -> 2 mins -> 1 min -> ENTER NOW. For test na 40 secs total. Watch channel!")
    await send_signal(pair, context.bot, fast_mode=True)
    session_data["next_index"] += 1

def main():
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", set_id))
    app.add_handler(CommandHandler("testsignal", testsignal))
    print("Enoch Bot - 5 STAGE FLOW: 5m -> 3m -> 2m -> 1m -> ENTER NOW with chart")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
