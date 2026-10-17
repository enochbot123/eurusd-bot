import os, time, requests, threading, yfinance as yf, pandas as pd, numpy as np
from flask import Flask

# ===== 1. KEEP ALIVE FOR RENDER =====
app = Flask(__name__)
@app.route('/')
def home():
    return "BOT FIXED V3 LIVE - EUR/USD-OTC 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# ===== 2. TELEGRAM =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(f"Sent: {msg[:50]}")
    except Exception as e:
        print(f"Telegram Error: {e}")

# ===== 3. INDICATORS =====
def smma(series, period):
    # Smoothed Moving Average for Alligator
    return series.ewm(alpha=1/period, adjust=False).mean()

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ===== 4. TRADING LOGIC - OTC 24/7 =====
SYMBOL = "EUR/USD-OTC"
DATA_SYMBOL = "EURUSD=X" # Yahoo finance real data (OTC price follows real)
print(f"BOT FIXED V3 IS LIVE - Trading {SYMBOL}")

def get_signal():
    try:
        # Get 1min data
        df = yf.download(DATA_SYMBOL, period="1d", interval="1m", progress=False)
        if len(df) < 50:
            return None
        
        # Fix yfinance multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        close = df['Close']
        
        # Alligator
        df['jaw'] = smma(close, 13).shift(8)   # Blue
        df['teeth'] = smma(close, 8).shift(5)  # Red
        df['lips'] = smma(close, 5).shift(3)   # Green
        
        # RSI
        df['rsi'] = calculate_rsi(close, 14)
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        price = float(last['Close'])
        lips = float(last['lips'])
        teeth = float(last['teeth'])
        jaw = float(last['jaw'])
        rsi = float(last['rsi'])
        
        print(f"Scanning {SYMBOL} | Price: {price:.5f} | RSI: {rsi:.1f} | Lips: {lips:.5f}")
        
        # HIGH ACCURACY FILTER
        # BUY: Lips > Teeth > Jaw AND RSI 30-48 (not overbought, pulling back)
        if lips > teeth > jaw and 30 <= rsi <= 48 and prev['lips'] <= prev['teeth']:
            return f"🟢 *BUY {SYMBOL}*\nPrice: `{price:.5f}`\nRSI: {rsi:.1f}\nSetup: Alligator BUY cross + RSI Oversold\nExpiry: *3 MINUTES*\nConfidence: 75-85% 🔥"

        # SELL: Lips < Teeth < Jaw AND RSI 52-70
        if lips < teeth < jaw and 52 <= rsi <= 70 and prev['lips'] >= prev['teeth']:
            return f"🔴 *SELL {SYMBOL}*\nPrice: `{price:.5f}`\nRSI: {rsi:.1f}\nSetup: Alligator SELL cross + RSI Overbought\nExpiry: *3 MINUTES*\nConfidence: 75-85% 🔥"
            
        return None
    except Exception as e:
        print(f"Scan Error: {e}")
        return None

def trading_loop():
    time.sleep(5)
    send_telegram(f"✅ *BOT FIXED V3 IS LIVE!*\nNow trading *{SYMBOL}*\nMode: *Monday to Sunday 24/7*\nStrategy: Alligator + RSI High Accuracy\nBot is scanning now...")
    
    last_signal_time = 0
    while True:
        try:
            signal = get_signal()
            if signal:
                # Cooldown 10 minutes to avoid spam
                if time.time() - last_signal_time > 600:
                    send_telegram(f"⚠️ *SET TIME NOW - 1 MIN LEFT!*\n\n{signal}\n\nEntry in 1 min!")
                    # Send ENTER NOW after 50 seconds
                    time.sleep(50)
                    price_line = signal.split('\n')[1]
                    send_telegram(f"🚀 *ENTER NOW!!!*\n{signal}\nTrade: https://pocket-friends.com/r/8vcvh8wte5")
                    last_signal_time = time.time()
                else:
                    print("Signal found but on cooldown")
            
            time.sleep(60) # Scan every 60 sec
        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(20)

# ===== 5. START =====
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    trading_loop()
