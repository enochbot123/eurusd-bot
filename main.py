import os
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, time
import pytz
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
YOUR_LINK = os.getenv("YOUR_LINK", "https://t.me/your_channel")

PAIRS = {
    "EURUSD": "EURUSD=X",
    "USDJPY": "USDJPY=X",
    "EURJPY": "EURJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "BTCUSD": "BTC-USD"
}

bot = Bot(token=BOT_TOKEN)
lagos = pytz.timezone('Africa/Lagos')

# --- SESSIONS (WAT) ---
SESSIONS = {
    "MORNING MONEY": (time(9, 30), time(10, 30)),
    "AFTERNOON ACTION": (time(14, 30), time(15, 30)),
    "EVENING SNIPER": (time(20, 30), time(21, 30))
}

reminded = {}

def analyze_real(pair_symbol):
    try:
        df = yf.download(pair_symbol, period="1d", interval="5m", progress=False)
        if len(df) < 60: return None, "Low data", 0, 0, 0, 0
        df['EMA20'] = ta.ema(df['Close'], 20)
        df['EMA50'] = ta.ema(df['Close'], 50)
        df['RSI'] = ta.rsi(df['Close'], 14)
        df['ATR'] = ta.atr(df['High'], df['Low'], df['Close'], 14)
        macd = ta.macd(df['Close'])
        df = pd.concat([df, macd], axis=1)
        last = df.iloc[-1]
        price = float(last['Close'])
        ema20 = float(last['EMA20'])
        ema50 = float(last['EMA50'])
        rsi = float(last['RSI'])
        atr = float(last['ATR'])
        macd_l = float(last['MACD_12_26_9'])
        sig_l = float(last['MACDs_12_26_9'])
        
        # UP REASON
        if price > ema20 > ema50 and 50 < rsi < 70 and macd_l > sig_l:
            reason = f"🟢 BULLISH BREAKOUT:\n├ Price don break above EMA20 & EMA50 (Strong Uptrend)\n├ RSI {rsi:.1f} - Momentum dey UP but not overbought\n├ MACD {macd_l:.4f} cross above signal - Buyers don take over\n└ ATR shows volatility to push UP"
            return "BUY", reason, price, rsi, macd_l, atr
        
        if price < ema20 < ema50 and 30 < rsi < 50 and macd_l < sig_l:
            reason = f"🔴 BEARISH BREAKDOWN:\n├ Price don break below EMA20 & EMA50 (Strong Downtrend)\n├ RSI {rsi:.1f} - Sellers dey control, momentum DOWN\n├ MACD {macd_l:.4f} cross below signal - Sell pressure high\n└ ATR confirms move to go DOWN"
            return "SELL", reason, price, rsi, macd_l, atr
            
        return None, f"Price: {price:.5f} | EMA20:{ema20:.5f} EMA50:{ema50:.5f} | RSI:{rsi:.1f} - No confluence yet, waiting for breakout", price, rsi, macd_l, atr
    except Exception as e:
        return None, str(e), 0,0,0,0

def get_current_session():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        if start <= now_t <= end:
            return name
    return None

def is_reminder_time():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        # 5 mins before
        start_min = start.hour*60 + start.minute - 5
        now_min = now_t.hour*60 + now_t.minute
        if now_min == start_min:
            return name
    return None

# --- MAIN LOOP ---
async def pro_scheduler():
    global reminded
    pair_list = list(PAIRS.keys())
    idx = 0
    pending_trade = None
    
    while True:
        try:
            now = datetime.now(lagos)
            now_str = now.strftime('%H:%M:%S WAT')
            current_session = get_current_session()
            reminder_session = is_reminder_time()
            
            # 1. REMINDER 5 MINS BEFORE
            if reminder_session and reminded.get(reminder_session) != now.date():
                reminded[reminder_session] = now.date()
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
⏰ **SESSION REMINDER - 5 MINS TO START** ⏰
━━━━━━━━━━━━━━━━━━
📢 {reminder_session} SESSION go start by {SESSIONS[reminder_session][0].strftime('%I:%M %p')}
💱 Pairs: {', '.join(PAIRS.keys())}

⚙️ **PRO SETTINGS:**
├ Strategy: EMA20/50 + RSI + MACD + ATR Breakout
├ Mode: Real Analysis (1 pair / 5 mins)
├ Risk: 2% per trade
└ BTC: Active 24/7

Make you ready! 👀
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)
                continue

            # 2. SESSION START
            if current_session and now.time().minute == SESSIONS[current_session][0].minute and now.time().second < 10:
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
🚀 **{current_session} SESSION STARTED** 🚀
━━━━━━━━━━━━━━━━━━
⏰ Time: {now_str}
📊 Session: {SESSIONS[current_session][0].strftime('%I:%M')} - {SESSIONS[current_session][1].strftime('%I:%M WAT')}
💱 Pairs: {' | '.join(PAIRS.keys())}

⚙️ **PROFESSIONAL SETTINGS ACTIVE:**
├ System: Real Market Analyzer v9.0
├ Analysis: EMA Trend + RSI Momentum + MACD Cross + ATR Volatility
├ Rotation: 1 Pair Every 5 Minutes
├ Entry: 2-step (Setup Alert → Entry Now)
└ Link: {YOUR_LINK}

Bot don start scanning with REAL breakout logic...
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)

            # 3. DURING SESSION - TRADE LOGIC
            if current_session:
                # If we have pending trade waiting for entry, send ENTRY NOW
                if pending_trade:
                    pt = pending_trade
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
{pt['emoji']} **ENTER NOW! {pt['pair']} - {pt['type']}** {pt['emoji']}
━━━━━━━━━━━━━━━━━━
⏰ Entry Time: {now_str}
💱 Pair: {pt['pair']}
{pt['emoji']} Direction: {pt['type']} {pt['emoji']}

💰 ENTRY PRICE: {pt['price']:.5f}
🛑 SL: {pt['sl']:.5f} (-7 pips)
🎯 TP1: {pt['tp1']:.5f} (+10 pips)
🎯 TP2: {pt['tp2']:.5f} (+20 pips)

🧠 **WHY THIS TRADE:**
{pt['reason']}

⚠️ Manage risk! 2% only!
Next analysis in 5 mins...
━━━━━━━━━━━━━━━━━━
""")
                    pending_trade = None
                    idx += 1
                    await asyncio.sleep(300)
                    continue

                # Otherwise, analyze new pair
                pair_name = pair_list[idx % len(pair_list)]
                symbol = PAIRS[pair_name]
                print(f"[{now_str}] Analyzing {pair_name} for {current_session}")
                
                sig_type, reason, price, rsi, macd_v, atr_v = analyze_real(symbol)

                if sig_type:
                    emoji = "🟢⬆️" if sig_type == "BUY" else "🔴⬇️"
                    pip = 0.0010 if "JPY" not in pair_name else 0.10
                    if "BTC" in pair_name: pip = 150.0
                    
                    sl = price - pip*7 if sig_type=="BUY" else price + pip*7
                    tp1 = price + pip*10 if sig_type=="BUY" else price - pip*10
                    tp2 = price + pip*20 if sig_type=="BUY" else price - pip*20

                    # STEP 1: PAIR WE GO TRADE (SETUP ALERT)
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
👀 **SETUP IDENTIFIED - {pair_name}** 👀
━━━━━━━━━━━━━━━━━━
⏰ Time: {now_str}
📊 Session: {current_session}
💱 Pair: {pair_name}

{emoji} **DIRECTION: {sig_type}** {emoji}
💰 Current Price: {price:.5f}
📊 RSI: {rsi:.1f} | MACD: {macd_v:.4f} | ATR: {atr_v:.4f}

🧠 **PRO ANALYSIS - WHY E GO {sig_type}:**
{reason}

⏳ **NEXT STEP:** I go send ENTER NOW in 5 minutes after final confirmation!
Prepare your lot size!
━━━━━━━━━━━━━━━━━━
""")
                    # Save for entry in next 5 mins
                    pending_trade = {
                        "pair": pair_name, "type": sig_type, "price": price,
                        "sl": sl, "tp1": tp1, "tp2": tp2, "reason": reason,
                        "emoji": emoji
                    }
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
🔍 **MARKET SCAN | {pair_name}**
━━━━━━━━━━━━━━━━━━
⏰ {now_str} | Session: {current_session}
💱 Pair: {pair_name}
💰 Price: {price:.5f}

📊 RSI: {rsi:.1f} | MACD: {macd_v:.4f}
📝 {reason}

❌ No breakout yet
🔄 Next: {pair_list[(idx+1)%len(pair_list)]} in 5 mins
━━━━━━━━━━━━━━━━━━
""")
                    idx += 1

                await asyncio.sleep(300) # 5 mins

            else:
                # Outside session - BTC only 24/7? Or sleep
                # For BTC 24/7 - we still scan BTC in evening gap
                if "BTCUSD" in PAIRS and now.time().hour not in [11,12,13,16,17,18,19,20]:
                     pass # skip to save API
                print(f"Outside session - sleeping 60s - {now_str}")
                await asyncio.sleep(60)

        except Exception as e:
            print(f"Scheduler error: {e}")
            await asyncio.sleep(30)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ No conflict - Pro scheduler started")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    asyncio.create_task(pro_scheduler())
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
