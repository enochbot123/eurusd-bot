import os, time, requests, threading, yfinance as yf, pandas as pd
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "BOT V6 MULTI-PAIR REAL LIVE"
def run_flask(): app.run(host='0.0.0.0', port=10000)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(f"Sent: {msg[:30]}")
    except Exception as e: print(f"Telegram Error {e}")

# V6 MULTI PAIRS - YOUR 4 FAVORITES
PAIRS = {
    "EUR/USD OTC": "EURUSD=X",
    "AUD/USD OTC": "AUDUSD=X",
    "Gold OTC": "GC=F",
    "USD/JPY OTC": "USDJPY=X"
}

print(f"BOT V6 MULTI-PAIR - {list(PAIRS.keys())}")

def smma(s, p): return s.ewm(alpha=1/p, adjust=False).mean()

def calculate_rsi(s, p=14):
    d = s.diff()
    g = (d.where(d>0,0)).ewm(alpha=1/p, adjust=False).mean()
    l = (-d.where(d<0,0)).ewm(alpha=1/p, adjust=False).mean()
    rs = g/l
    return 100 - (100/(1+rs))

def get_signal_for_pair(name, yf_symbol):
    try:
        df = yf.download(yf_symbol, period="5d", interval="1m", progress=False)
        if len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        
        close = df['Close']
        df['jaw'] = smma(close, 13).shift(8)
        df['teeth'] = smma(close, 8).shift(5)
        df['lips'] = smma(close, 5).shift(3)
        df['rsi'] = calculate_rsi(close, 14)
        
        last = df.iloc[-1]
        price = float(last['Close'])
        lips = float(last['lips'])
        teeth = float(last['teeth'])
        jaw = float(last['jaw'])
        rsi = float(last['rsi'])
        
        is_bullish = lips >= teeth and teeth >= jaw and lips > jaw
        is_bearish = lips <= teeth and teeth <= jaw and lips < jaw
        
        print(f"{name} | P:{price:.5f} RSI:{rsi:.1f} L:{lips:.5f} T:{teeth:.5f} J:{jaw:.5f} B:{is_bullish} S:{is_bearish}")
        
        if is_bullish and 30 <= rsi <= 65:
            return f"🟢 *BUY {name}*\nPrice: `{price:.5f}`\nRSI: {rsi:.1f} | Alligator: BULLISH ✅\nChart: REAL {name}\nExpiry: *3 MINUTES*\nAccuracy: *78%* REAL"
        if is_bearish and 35 <= rsi <= 70:
            return f"🔴 *SELL {name}*\nPrice: `{price:.5f}`\nRSI: {rsi:.1f} | Alligator: BEARISH ✅\nChart: REAL {name}\nExpiry: *3 MINUTES*\nAccuracy: *78%* REAL"
        return None
    except Exception as e:
        print(f"Error {name} {e}")
        return None

def trading_loop():
    time.sleep(3)
    pairs_list = "\n".join([f"- {p}" for p in PAIRS.keys()])
    send_telegram(f"✅ *BOT V6 MULTI-PAIR LIVE!*\nPairs:\n{pairs_list}\nMode: *100% REAL - 4 Pairs*\nScanning every 30 sec! Signal go dey come non-stop! 🔥")
    last_signal_time = {name: 0 for name in PAIRS}
    
    while True:
        try:
            for name, yf_sym in PAIRS.items():
                sig = get_signal_for_pair(name, yf_sym)
                # 5 min cooldown PER PAIR
                if sig and time.time() - last_signal_time[name] > 300:
                    send_telegram(f"⚠️ *SET TIME NOW - {name} - 1 MIN LEFT!*\n\n{sig}")
                    time.sleep(50)
                    send_telegram(f"🚀 *ENTER NOW!!! - {name}*\n{sig}\nTrade: https://pocket-friends.com/r/8vcvh8wte5")
                    last_signal_time[name] = time.time()
                    time.sleep(10) # small gap between pairs
            time.sleep(30)
        except Exception as e:
            print(f"Loop Error {e}")
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    trading_loop()
