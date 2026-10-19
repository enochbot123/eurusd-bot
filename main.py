import os
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, time
import pytz
from telegram import Bot
from telegram.ext import Application
import asyncio
from gtts import gTTS

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
YOUR_LINK = os.getenv("YOUR_LINK", "https://t.me/your_channel")

# ✅ PAIRS - NO GBP, NO GOLD, BTC ACTIVE 24/7
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

# --- 3 SESSIONS ---
SESSIONS = {
    "🌅 MORNING MONEY": (time(9, 30), time(10, 30)),
    "🔥 AFTERNOON ACTION": (time(14, 30), time(15, 30)),
    "🌙 EVENING SNIPER": (time(20, 30), time(21, 30))
}

reminded = {}

# --- REAL MARKET ANALYZER ---
def analyze_real(pair_symbol):
    try:
        df = yf.download(pair_symbol, period="1d", interval="5m", progress=False)
        if len(df) < 60:
            return None, "Low data", 0, 0, 0, 0, 0, 0
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
        
        # 🟢 BUY
        if price > ema20 > ema50 and 50 < rsi < 70 and macd_l > sig_l:
            reason = f"🟢 BULLISH BREAKOUT CONFIRMED:\n├ 💹 Price don break above EMA20 ({ema20:.5f}) & EMA50 ({ema50:.5f}) - Strong Uptrend\n├ 📈 RSI {rsi:.1f} - Momentum dey UP but not overbought\n├ 📊 MACD {macd_l:.4f} cross above signal {sig_l:.4f} - Buyers don take over\n└ ⚡ ATR {atr:.5f} - Volatility dey support UP move"
            return "BUY", reason, price, rsi, macd_l, atr, ema20, ema50
        
        # 🔴 SELL
        if price < ema20 < ema50 and 30 < rsi < 50 and macd_l < sig_l:
            reason = f"🔴 BEARISH BREAKDOWN CONFIRMED:\n├ 📉 Price don break below EMA20 ({ema20:.5f}) & EMA50 ({ema50:.5f}) - Strong Downtrend\n├ 📉 RSI {rsi:.1f} - Sellers dey control, momentum DOWN\n├ 📊 MACD {macd_l:.4f} cross below signal {sig_l:.4f} - Sell pressure high\n└ ⚡ ATR {atr:.5f} - Confirms move to go DOWN"
            return "SELL", reason, price, rsi, macd_l, atr, ema20, ema50
            
        return None, f"⏳ No confluence yet - Waiting for breakout\n├ 💰 Price: {price:.5f}\n├ 📊 EMA20: {ema20:.5f} | EMA50: {ema50:.5f}\n├ 📈 RSI: {rsi:.1f}\n└ 📊 MACD: {macd_l:.4f}", price, rsi, macd_l, atr, ema20, ema50
    except Exception as e:
        return None, str(e), 0,0,0,0,0,0

def get_current_session():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        if start <= now_t <= end:
            return name
    return None

def is_reminder_time():
    now_t = datetime.now(lagos).time()
    for name, (start, end) in SESSIONS.items():
        start_min = start.hour*60 + start.minute - 5
        now_min = now_t.hour*60 + now_t.minute
        if now_min == start_min:
            return name
    return None

# --- VOICE - SHORT 2 SEC ALARM ---
async def send_voice_entry(pair, sig_type):
    try:
        if "BUY" in sig_type:
            voice_text = f"{pair} Buy now! Buy now! {pair} Buy!"
        else:
            voice_text = f"{pair} Sell now! Sell now! {pair} Sell!"
        
        tts = gTTS(text=voice_text, lang='en', tld='com', slow=False)
        filename = f"/tmp/{pair}.mp3"
        tts.save(filename)
        
        with open(filename, 'rb') as audio:
            await bot.send_voice(chat_id=CHANNEL_ID, voice=audio, caption=f"🎙️ ⏰ {pair} {sig_type} ALARM!")
        print(f"✅ Voice sent {pair}")
    except Exception as e:
        print(f"Voice error: {e}")

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
            now_date = now.strftime('%d-%m-%Y')
            current_session = get_current_session()
            reminder_session = is_reminder_time()
            
            # 1. ⏰ REMINDER 5 MINS BEFORE
            if reminder_session and reminded.get(reminder_session) != now.date():
                reminded[reminder_session] = now.date()
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
⏰ **SESSION REMINDER - 5 MINS TO GO** ⏰
━━━━━━━━━━━━━━━━━━
📢 Session: {reminder_session}
🕘 Start Time: {SESSIONS[reminder_session][0].strftime('%I:%M %p')} WAT
⏰ Current Time: {now_str}
📅 Date: {now_date}

💱 Pairs To Trade:
├ EURUSD
├ USDJPY
├ EURJPY
├ AUDUSD
├ USDCAD
└ BTCUSD (24/7)

⚙️ **PRO SETTINGS:**
├ 🧠 Strategy: EMA20/50 + RSI + MACD + ATR
├ 🔄 Mode: 1 Pair Every 5 Minutes
├ ⚠️ Risk: 2% Per Trade
└ 🔗 {YOUR_LINK}

👀 Make you ready - Bot go start soon!
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)
                continue

            # 2. 🚀 SESSION START
            if current_session and now.time().minute == SESSIONS[current_session][0].minute and now.time().second < 15:
                await bot.send_message(chat_id=CHANNEL_ID, text=f"""
🚀 **{current_session} SESSION STARTED** 🚀
━━━━━━━━━━━━━━━━━━
⏰ Time: {now_str}
📅 Date: {now_date}
🕘 Session: {SESSIONS[current_session][0].strftime('%I:%M')} - {SESSIONS[current_session][1].strftime('%I:%M WAT')}

💱 **PAIRS:**
├ 💱 EURUSD
├ 💱 USDJPY
├ 💱 EURJPY
├ 💱 AUDUSD
├ 💱 USDCAD
└ ₿ BTCUSD (24/7 Active)

⚙️ **PROFESSIONAL SETTINGS ACTIVE:**
├ 🧠 System: Real Market Analyzer v10.0
├ 📊 Analysis: EMA Trend + RSI Momentum + MACD Cross + ATR Volatility
├ 🔄 Rotation: 1 Pair Every 5 Minutes
├ 📝 Entry: 2-Step (Setup → Enter Now + Voice)
├ ⏰ Timezone: WAT (Lagos)
└ 🔗 {YOUR_LINK}

👀 Bot don start scanning with REAL breakout logic...
━━━━━━━━━━━━━━━━━━
""")
                await asyncio.sleep(60)

            # 3. DURING SESSION
            if current_session:
                # ENTER NOW
                if pending_trade:
                    pt = pending_trade
                    emoji = pt['emoji']
                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
{emoji} **ENTER NOW! {pt['pair']} - {pt['type']}** {emoji}
━━━━━━━━━━━━━━━━━━
⏰ Entry Time: {now_str}
📅 Date: {now_date}
⏰ Session: {current_session}
💱 Pair: {pt['pair']}
{emoji} Direction: {pt['type']} {emoji}

💰 ENTRY PRICE: {pt['price']:.5f}
🛑 STOP LOSS: {pt['sl']:.5f} (-7 pips)
🎯 TAKE PROFIT 1: {pt['tp1']:.5f} (+10 pips)
🎯 TAKE PROFIT 2: {pt['tp2']:.5f} (+20 pips)

🧠 **WHY THIS TRADE GO {pt['type']}:**
{pt['reason']}

📊 **INDICATORS:**
├ ⏰ Time: {now_str}
├ 💰 Price: {pt['price']:.5f}
├ 📈 RSI: {pt['rsi']:.1f}
├ 📊 MACD: {pt['macd']:.4f}
└ ⚡ ATR: {pt['atr']:.5f}

⚠️ Risk: Manage 2% only!
⏰ Next Analysis: In 5 minutes...
🔗 {YOUR_LINK}
━━━━━━━━━━━━━━━━━━
""")
                    await send_voice_entry(pt['pair'], pt['type'])
                    pending_trade = None
                    idx += 1
                    await asyncio.sleep(300)
                    continue

                # ANALYZE ONE PAIR
                pair_name = pair_list[idx % len(pair_list)]
                symbol = PAIRS[pair_name]
                print(f"[{now_str}] Analyzing {pair_name}")
                
                sig_type, reason, price, rsi, macd_v, atr_v, ema20, ema50 = analyze_real(symbol)

                if sig_type:
                    emoji = "🟢⬆️" if sig_type == "BUY" else "🔴⬇️"
                    pip = 0.0010 if "JPY" not in pair_name else 0.10
                    if "BTC" in pair_name: pip = 150.0
                    sl = price - pip*7 if sig_type=="BUY" else price + pip*7
                    tp1 = price + pip*10 if sig_type=="BUY" else price - pip*10
                    tp2 = price + pip*20 if sig_type=="BUY" else price - pip*20

                    await bot.send_message(chat_id=CHANNEL_ID, text=f"""
👀 **SETUP IDENTIFIED - {pair_name}** 👀
━━━━━━━━━━━━━━━━━━
⏰ Time: {now_str}
📅 Date: {now_date}
⏰ Session: {current_session}
💱 Pair: {pair_name}

{emoji} **DIRECTION: {sig_type}** {emoji}
💰 Current Price: {price:.5f}
📊 EMA20: {ema20:.5f}
📊 EMA50: {ema50:.5f}
📈 RSI: {rsi:.1f}
📊 MACD: {macd_v:.4f}
⚡ ATR: {atr_v:.5f}

🧠 **PRO ANALYSIS - WHY E GO {sig_type}:**
{reason}

⏳ **NEXT STEP:**
├ ⏰ I go send ENTER NOW in 5 minutes
├ 🎙️ With
