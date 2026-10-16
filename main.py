import os, time, requests, pytz, yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home(): return "Enoch Bot V3 - REAL ANALYSIS LIVE!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
LINK = os.environ.get("POCKET_LINK")

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_analysis():
    try:
        # Get real EUR/USD data - last 1 hour, 1min candles
        data = yf.download("EURUSD=X", period="1d", interval="5m", progress=False)
        if len(data) < 20:
            return None, "Not enough data"
        
        close = data['Close']
        # Calculate EMA
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        
        # Calculate RSI 14
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_val = rsi.iloc[-1]
        
        price = float(close.iloc[-1])
        
        # REAL LOGIC
        if ema9 > ema21 and rsi_val < 70 and rsi_val > 45:
            signal = "BUY"
            reason = f"Uptrend (EMA9 {ema9:.5f} > EMA21 {ema21:.5f}) + RSI {rsi_val:.1f}"
            confidence = "HIGH" if rsi_val < 65 else "MEDIUM"
        elif ema9 < ema21 and rsi_val > 30 and rsi_val < 55:
            signal = "SELL"
            reason = f"Downtrend (EMA9 {ema9:.5f} < EMA21 {ema21:.5f}) + RSI {rsi_val:.1f}"
            confidence = "HIGH" if rsi_val > 35 else "MEDIUM"
        else:
            signal = "WAIT"
            reason = f"Market choppy - RSI {rsi_val:.1f}, EMA9/EMA21 close"
            confidence = "LOW"
            
        return {
            "signal": signal,
            "price": price,
            "rsi": float(rsi_val),
            "ema9": float(ema9),
            "ema21": float(ema21),
            "reason": reason,
            "confidence": confidence
        }, None
    except Exception as e:
        return None, str(e)

def loop():
    send("🚀 <b>Enoch Bot V3 UPGRADED!</b>\n✅ Now using REAL ANALYSIS\n📊 RSI + EMA + Live EUR/USD Price\n⏰ Signal every 5 mins")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            analysis, err = get_analysis()
            
            if err:
                print(f"Analysis error: {err}")
                time.sleep(60)
                continue
            
            if analysis['signal'] == "WAIT":
                msg = f"⏸️ <b>WAIT - No clear setup</b>\n💰 EUR/USD: {analysis['price']:.5f}\n📊 RSI: {analysis['rsi']:.1f} | {analysis['reason']}\n⏰ {now.strftime('%H:%M:%S')} Lagos"
                print(f"WAIT - RSI {analysis['rsi']:.1f}")
            else:
                msg = f"🔥 <b>{analysis['signal']} EUR/USD - 5 MIN</b>\n💰 Price: {analysis['price']:.5f}\n📊 RSI: {analysis['rsi']:.1f} | Confidence: {analysis['confidence']}\n🧠 {analysis['reason']}\n⏰ {now.strftime('%H:%M:%S')} Lagos\n🔗 Trade: {LINK}"
                print(f"{analysis['signal']} - {analysis['price']}")
            
            send(msg)
            time.sleep(300)  # 5 mins
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

loop()
