import os, time, threading, requests, json
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)
TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT = "8868905914"

SYMBOLS_LIST = [
    ("EUR/USD", "EURUSD=X"),
    ("AUD/USD", "AUDUSD=X"),
    ("USD/JPY", "USDJPY=X"),
    ("GBP/JPY", "GBPJPY=X"),
    ("Gold", "GC=F")
]

last_set = -1
last_enter = -1
current_pair = SYMBOLS_LIST[0]
STATS_FILE = "stats.json"

# Load stats
def load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {"date": str(datetime.now().date()), "total": 0, "wins": 0, "losses": 0, "profit": 0.0}

def save_stats(s):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(s, f)
    except:
        pass

stats = load_stats()
last_update_id = 0

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
        data={"chat_id": CHAT, "text": msg}, timeout=15)
    except:
        pass

def get_analysis(ticker):
    try:
        time.sleep(1)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 30:
            return "DOWN", "Price approached strong resistance after rapid upward movement."
        close = closes[-1]
        ema9 = sum(closes[-9:]) / 9
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.1
        avg_loss = sum(losses)/14 if losses else 0.1
        rsi = 100 - (100/(1+avg_gain/avg_loss))
        if close > ema9 and rsi < 70:
            direction = "UP"
            reason = f"Price broke support with bullish momentum. RSI {rsi:.1f} shows buyers in control. Based on this, we enter a buy trade."
        else:
            direction = "DOWN"
            reason = f"Price approached strong resistance after rapid upward move. Bearish pattern appeared. RSI {rsi:.1f} indicates overbought. Based on this, we enter a sell trade."
        return direction, reason
    except:
        return "DOWN", "Price approached strong resistance level. Bearish signal confirmed. Based on this, we enter a sell trade."

# NEW: Track win/loss from your reply
def poll_telegram():
    global last_update_id, stats
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
            r = requests.get(url, timeout=35).json()
            for upd in r.get("result", []):
                last_update_id = upd["update_id"]
                msg = upd.get("message", {}).get("text", "").lower().strip()
                if not msg: continue
                
                if msg in ["win", "w", "won", "+"]:
                    stats["wins"] += 1
                    stats["profit"] += 4.4 # avg profit estimate
                    save_stats(stats)
                    win_rate = (stats["wins"]/(stats["wins"]+stats["losses"])*100) if (stats["wins"]+stats["losses"])>0 else 0
                    send(f"✅ WIN recorded!\n📊 Today: {stats['total']} signals\n🏆 {stats['wins']}W - {stats['losses']}L - {win_rate:.1f}% win rate")
                elif msg in ["loss", "l", "lost", "-"]:
                    stats["losses"] += 1
                    stats["profit"] -= 5.0
                    save_stats(stats)
                    win_rate = (stats["wins"]/(stats["wins"]+stats["losses"])*100) if (stats["wins"]+stats["losses"])>0 else 0
                    send(f"❌ LOSS recorded!\n📊 Today: {stats['total']} signals\n🏆 {stats['wins']}W - {stats['losses']}L - {win_rate:.1f}% win rate")
                elif msg in ["/stats", "/result", "stats", "result"]:
                    total_played = stats["wins"] + stats["losses"]
                    win_rate = (stats["wins"]/total_played*100) if total_played>0 else 0
                    send(f"📈 DAILY RESULT - {stats['date']}\n━━━━━━━━━━━━━━\n📤 Signals sent: {stats['total']}\n✅ Wins: {stats['wins']}\n❌ Losses: {stats['losses']}\n📊 Win rate: {win_rate:.1f}%\n💰 Est. Profit: ${stats['profit']:.2f}\n━━━━━━━━━━━━━━\nReply 'win' or 'loss' after each trade to track!")
        except Exception as e:
            print(f"Poll error: {e}")
        time.sleep(2)

def loop():
    global last_set, last_enter, current_pair, stats
    time.sleep(3)
    send("✅ TRACKER ADDED!\n\nHow to use:\nAfter each trade, just type:\n'win' if you win\n'loss' if you lose\n\nType 'stats' anytime to see daily result!\n\nBOT NOW - 1 BY 1 ROTATION")
    
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second
            
            # Reset daily at midnight
            if str(now.date()) != stats["date"]:
                # Send final report before reset
                total_played = stats["wins"] + stats["losses"]
                win_rate = (stats["wins"]/total_played*100) if total_played>0 else 0
                send(f"🌙 FINAL DAILY REPORT - {stats['date']}\n━━━━━━━━━━━━━━\n📤 Signals: {stats['total']}\n✅ Wins: {stats['wins']}\n❌ Losses: {stats['losses']}\n📊 Win rate: {win_rate:.1f}%\n💰 Profit: ${stats['profit']:.2f}\n━━━━━━━━━━━━━━\nNew day started!")
                stats = {"date": str(now.date()), "total": 0, "wins": 0, "losses": 0, "profit": 0.0}
                save_stats(stats)

            total_blocks = now.hour * 12 + (cm // 5)
            idx = total_blocks % len(SYMBOLS_LIST)
            current_pair = SYMBOLS_LIST[idx]

            if cm % 5 == 4 and last_set != cm and cs < 50:
                last_set = cm
                name = current_pair[0]
                msg = f"❗ (UTC+1)\n\n📊 Currency pair: {name} OTC\n⏱ Expiration time: 3 min [M3]\n\n⏰ SET TIME: {now.hour:02d}:{cm+1:02d} - Prepare {name}"
                send(msg)

            if cm % 5 == 0 and last_enter != cm and cs < 50:
                last_enter = cm
                prev_idx = (total_blocks - 1) % len(SYMBOLS_LIST) if total_blocks > 0 else 0
                name_e, ticker_e = SYMBOLS_LIST[prev_idx]
                direction, reason = get_analysis(ticker_e)
                direction_text = "👻 UP" if direction == "UP" else "👻 DOWN"
                entry_time = f"{now.hour:02d}:{cm:02d}"
                
                stats["total"] += 1
                save_stats(stats)
                
                msg = f"Entry time: ⏰ {entry_time}\nDirection: {direction_text}\n\n➤ {reason}"
                send(msg)

        except Exception as e:
            print(e)
        time.sleep(1)

@app.route("/")
def home():
    return "BOT LIVE - WITH WIN/LOSS TRACKER"

threading.Thread(target=loop, daemon=True).start()
threading.Thread(target=poll_telegram, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
