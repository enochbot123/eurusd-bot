import os
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, time
import pytz
from telegram import Bot
from telegram.ext import Application
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

SESSIONS = {
    "🌅 MORNING MONEY": (time(9, 30), time(10, 30)),
    "🔥 AFTERNOON ACTION": (time(14, 30), time(15, 30)),
    "🌙 EVENING SNIPER": (time(20, 30), time(21, 30))
}

reminded = {}

def analyze_real(pair_symbol):
    try:
        df = yf.download(pair_symbol, period="1d", interval="5m", progress=False)
        if len(df) < 60: return None, "Low data", 0,0,0,0,0,0
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
        
        if price > ema20 > ema50 and 50 < rsi < 70 and macd_l > sig_l:
            reason = f"🟢 BULLISH BREAKOUT:\n├ Price don break above EMA20 & EMA50\n├ RSI {rsi:.1f} momentum UP\n├ MACD bullish cross\n└ ATR support UP move"
            return "BUY", reason, price, rsi, macd_l, atr, ema20, ema50
        
        if price < ema20 < ema50 and 30 < rsi < 50 and macd_l < sig_l:
            reason = f"🔴 BEARISH BREAKDOWN:\n├ Price don break below EMA20 & EMA50\n├ RSI {rsi:.1f} sellers control\n├ MACD bearish cross\n└ ATR confirms DOWN move"
            return "SELL", reason, price, rsi, macd_l, atr, ema20, ema50
            
        return None, f"Waiting breakout - Price {price:.5f} | RSI {rsi:.1f}", price, rsi, macd_l, atr, ema20, ema50
    except Exception as e:
        return None, str(e), 0,0,0,0,0,0

def get_current_session():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        if start <= now_t <= end: return name
    return None

def is_reminder_time():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        start_min = start.hour*60 + start.minute - 5
        now_min = now_t.hour*60 + now_t.minute
        if now_min == start_min: return name
    return None

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
            
            if reminder_session and reminded.get(reminder_session) != now.date():
                reminded[reminder_session] = now.date()
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
⏰ SESSION REMINDER - 5 MINS TO GO ⏰
━━━━━━━━━━━━━━━━━━
📢 {reminder_session}
🕘 Start: {SESSIONS[reminder_session][0].strftime('%I:%M %p')} WAT
⏰ Now: {now_str}
💱 Pairs: {', '.join(PAIRS.keys())}
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)
                continue

            if current_session and now.time().minute == SESSIONS[current_session][0].minute and now.time().second < 15:
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
🚀 {current_session} SESSION STARTED 🚀
━━━━━━━━━━━━━━━━━━
⏰ {now_str}
💱 Pairs: {' | '.join(PAIRS.keys())}
⚙️ PRO ANALYZER ACTIVE
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)

            if current_session:
                if pending_trade:
                    pt = pending_trade
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
{pt['emoji']} ENTER NOW! {pt['pair']} - {pt['type']} {pt['emoji']}
━━━━━━━━━━━━━━━━━━
⏰ {now_str}
💱 {pt['pair']} | {pt['type']}
💰 ENTRY: {pt['price']:.5f}
🛑 SL: {pt['sl']:.5f}
🎯 TP1: {pt['tp1']:.5f}
🎯 TP2: {pt['tp2']:.5f}
🧠 {pt['reason']}
━━━━━━━━━━━━━━━━━━
""")
                    pending_trade = None
                    idx += 1
                    await asyncio.sleep(300)
                    continue

                pair_name = pair_list[idx % len(pair_list)]
                symbol = PAIRS[pair_name]
                sig_type, reason, price, rsi, macd_v, atr_v, ema20, ema50 = analyze_real(symbol)

                if sig_type:
                    emoji = "🟢⬆️" if sig_type == "BUY" else "🔴⬇️"
                    pip = 0.0010 if "JPY" not in pair_name else 0.10
                    if "BTC" in pair_name: pip = 150.0
                    sl = price - pip*7 if sig_type=="BUY" else price + pip*7
                    tp1 = price + pip*10 if sig_type=="BUY" else price - pip*10
                    tp2 = price + pip*20 if sig_type=="BUY" else price - pip*20

                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
👀 SETUP IDENTIFIED - {pair_name} 👀
━━━━━━━━━━━━━━━━━━
⏰ {now_str} | {current_session}
💱 {pair_name} | {emoji} {sig_type}
💰 Price: {price:.5f}
🧠 {reason}
⏳ NEXT: ENTER NOW in 5 mins
━━━━━━━━━━━━━━━━━━
""")
                    pending_trade = {"pair": pair_name, "type": sig_type, "price": price, "sl": sl, "tp1": tp1, "tp2": tp2, "reason": reason, "emoji": emoji}
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
🔍 SCAN | {pair_name} | ⏰ {now_str}
💰 {price:.5f} | RSI {rsi:.1f}
📝 {reason}
❌ No breakout - Next in 5 mins
""")
                    idx += 1
                await asyncio.sleep(300)
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(30)

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    await bot.delete_webhook(drop_pending_updates=True)
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    asyncio.create_task(pro_scheduler())
    while True: await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
