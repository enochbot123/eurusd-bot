import os, time, requests, threading, yfinance as yf, pandas as pd
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home(): return "V6 LIVE"
def run_flask(): app.run(host='0.0.0.0', port=10000)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass
PAIRS = {"EUR/USD OTC": "EURUSD=X", "AUD/USD OTC": "AUDUSD=X", "Gold OTC": "GC=F", "USD/JPY OTC": "USDJPY=X"}
def smma(s, p): return s.ewm(alpha=1/p, adjust=False).mean()
def calculate_rsi(s, p=14):
    d = s.diff(); g = (d.where(d>0,0)).ewm(alpha=1/p, adjust=False).mean(); l = (-d.where(d<0,0)).ewm(alpha=1/p, adjust=False).mean(); rs = g/l; return 100 - (100/(1+rs))
def get_signal(name, yf_sym):
    try:
        df = yf.download(yf_sym, period="5d", interval="1m", progress=False)
        if len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        close = df['Close']; df['jaw'] = smma(close, 13).shift(8); df['teeth'] = smma(close, 8).shift(5); df['lips'] = smma(close, 5).shift(3); df['rsi'] = calculate_rsi(close, 14)
        last = df.iloc[-1]; price = float(last['Close']); lips = float(last['lips']); teeth = float(last['teeth']); jaw = float(last['jaw']); rsi = float(last['rsi'])
        is_bull = lips >= teeth and teeth >= jaw and lips > jaw; is_bear = lips <= teeth and teeth <= jaw and lips < jaw
        if is_bull and 30 <= rsi <= 65: return f"🟢 BUY {name} Price {price:.5f} RSI {rsi:.1f} REAL 3 MIN"
        if is_bear and 35 <= rsi <= 70: return f"🔴 SELL {name} Price {price:.5f} RSI {rsi:.1f} REAL 3 MIN"
        return None
    except: return None
def trading_loop():
    time.sleep(5)
    send_telegram("✅ V6 MULTI-PAIR BOT LIVE! 4 pairs scanning!"); last = {n:0 for n in PAIRS}
    while True:
        try:
            for name, sym in PAIRS.items():
                sig = get_signal(name, sym)
                if sig and time.time() - last[name] > 300:
                    send_telegram(f"⚠️ SET TIME NOW 1 MIN LEFT!\n\n{sig}"); time.sleep(50); send_telegram(f"🚀 ENTER NOW!!!\n{sig}"); last[name] = time.time(); time.sleep(10)
            time.sleep(30)
        except: time.sleep(15)
if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    trading_loop()
