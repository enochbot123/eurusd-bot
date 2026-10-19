import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, time
import pytz
from telegram import Bot
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

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(series):
    ema12 = ema(series, 12)
    ema26 = ema(series, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    return macd_line, signal

def atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def analyze_real(pair_symbol):
    try:
        df = yf.download(pair_symbol, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 60: return None, "Low data", 0,0,0,0,0,0
        close = df['Close']
        high = df['High']
        low = df['Low']
        df['EMA20'] = ema(close, 20)
        df['EMA50'] = ema(close, 50)
        df['RSI'] = rsi(close, 14)
        df['ATR'] = atr(high, low, close, 14)
        macd_line, signal_line = macd(close)
        df['MACD'] = macd_line
        df['SIGNAL'] = signal_line
        last = df.iloc[-1]
        price = float(last['Close'])
        ema20 = float(last['EMA20'])
        ema50 = float(last['EMA50'])
        rsi_v = float(last['RSI'])
        atr_v = float(last['ATR'])
        macd_l = float(last['MACD'])
        sig_l = float(last['SIGNAL'])
        
        if price > ema20 > ema50 and 50 < rsi_v < 70 and macd_l > sig_l:
            reason = f"🟢 BULLISH BREAKOUT:\n├ Price break above EMA20 & EMA50\n├ RSI {rsi_v:.1f} UP momentum\n├ MACD bullish cross\n└ ATR support UP"
            return "BUY", reason, price, rsi_v, macd_l, atr_v, ema20, ema50
        if price < ema20 < ema50 and 30 < rsi_v < 50 and macd_l < sig_l:
            reason = f"🔴 BEARISH BREAKDOWN:\n├ Price break below EMA20 & EMA50\n├ RSI {rsi_v:.1f} sellers control\n├ MACD bearish cross\n└ ATR confirms DOWN"
            return "SELL", reason, price, rsi_v, macd_l, atr_v, ema20, ema50
        return None, f"Waiting breakout - Price {price:.5f} | RSI {rsi_v:.1f}", price, rsi_v, macd_l, atr_v, ema20, ema50
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
    
    # ✅ FIX CONFLICT - Delete webhook once at start
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook deleted - No conflict")
    except Exception as e:
        print(f"Delete webhook error: {e}")

    while True:
        try:
            now = datetime.now(lagos)
            now_str = now.strftime('%H:%M:%S WAT')
            current_session = get_current_session()
            reminder_session = is_reminder_time()
            
            if reminder_session and reminded.get(reminder_session) != now.date():
                reminded[reminder_session] = now.date()
                await bot.send_message(chat_id=CHANNEL_ID, text=f"⏰ SESSION REMINDER - 5 MINS TO GO ⏰\n📢 {reminder_session}\n🕘 Start: {SESSIONS[reminder_session][0].strftime('%I:%M %p')} WAT\n⏰ Now: {now_str}")
                await asyncio.sleep(60)
                continue

            if current_session and now.time().minute == SESSIONS[current_session][0].minute and now.time().second < 15:
                await bot.send_message(chat_id=CHANNEL_ID, text=f"🚀 {current_session} SESSION STARTED 🚀\n⏰ {now_str}\n💱 Pairs: {' | '.join(PAIRS.keys())}")
                await asyncio.sleep(60)

            if current_session:
                if pending_trade:
                    pt = pending_trade
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"{pt['emoji']} ENTER NOW! {pt['pair']} - {pt['type']} {pt['emoji']}\n━━━━━━━━━━\n⏰ {now_str}\n💱 {pt['pair']}\n💰 ENTRY: {pt['price']:.5f}\n🛑 SL: {pt['sl']:.5f}\n🎯 TP1: {pt['tp1']:.5f}\n🎯 TP2: {pt['tp2']:.5f}\n🧠 {pt['reason']}")
                    pending_trade = None
                    idx += 1
                    await asyncio.sleep(300)
                    continue

                pair_name = pair_list[idx % len(pair_list)]
                symbol = PAIRS[pair_name]
                sig_type, reason, price, rsi_v, macd_v, atr_v, ema20, ema50 = analyze_real(symbol)

                if sig_type:
                    emoji = "🟢⬆️" if sig_type == "BUY" else "🔴⬇️"
                    pip = 0.0010 if "JPY" not in pair_name else 0.10
                    if "BTC" in pair_name: pip = 150.0
                    sl = price - pip*7 if sig_type=="BUY" else price + pip*7
                    tp1 = price + pip*10 if sig_type=="BUY" else price - pip*10
                    tp2 = price + pip*20 if sig_type=="BUY" else price - pip*20
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"👀 SETUP IDENTIFIED - {pair_name} 👀\n⏰ {now_str} | {current_session}\n💱 {pair_name} | {emoji} {sig_type}\n💰 Price: {price:.5f}\n🧠 {reason}\n⏳ NEXT: ENTER NOW in 5 mins")
                    pending_trade = {"pair": pair_name, "type": sig_type, "price": price, "sl": sl, "tp1": tp1, "tp2": tp2, "reason": reason, "emoji": emoji}
                else:
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"🔍 SCAN | {pair_name} | ⏰ {now_str}\n💰 {price:.5f} | RSI {rsi_v:.1f}\n📝 {reason}\n❌ No breakout - Next in 5 mins")
                    idx += 1
                await asyncio.sleep(300)
            else:
                await asyncio.sleep(60)
        except Exception as e:
            print(f"Scheduler error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(pro_scheduler())
