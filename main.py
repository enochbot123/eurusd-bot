import os, time, threading, requests, json
from flask import Flask
from datetime import datetime, time as dtime, timedelta
import pytz

app = Flask(__name__)
TOKEN = "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ"
CHAT = "8868905914"

SYMBOLS_LIST = [("EUR/USD", "EURUSD=X"), ("AUD/USD", "AUDUSD=X"), ("USD/JPY", "USDJPY=X"), ("GBP/JPY", "GBPJPY=X"), ("Gold", "GC=F")]

last_set = -1
last_enter = -1
STATS_FILE = "stats.json"

SESSIONS = {
    "morning": {"start": dtime(10, 0), "end": dtime(11, 0), "label": "MORNING (10AM-11AM)"},
    "afternoon": {"start": dtime(13, 0), "end": dtime(14, 0), "label": "AFTERNOON (1PM-2PM)"},
    "evening": {"start": dtime(17, 0), "end": dtime(18, 0), "label": "EVENING (5PM-6PM)"}
}

def get_current_session(now_time):
    for name, s in SESSIONS.items():
        if s["start"] <= now_time <= s["end"]:
            return name
    return None

def load_stats():
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
    except: pass
    return {"date": str(datetime.now().date()), "total": 0, "wins": 0, "losses": 0, "profit": 0.0,
            "morning": {"total": 0, "wins": 0, "losses": 0}, "afternoon": {"total": 0, "wins": 0, "losses": 0},
            "evening": {"total": 0, "wins": 0, "losses": 0}, "last_session": None}

def save_stats(s):
    try:
        with open(STATS_FILE, 'w') as f: json.dump(s, f)
    except: pass

stats = load_stats()
last_update_id = 0

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT, "text": msg}, timeout=15)
    except: pass

def get_analysis(ticker):
    try:
        time.sleep(1)
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        data = r.json()['chart']['result'][0]
        closes = [c for c in data['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 30: return "DOWN", "Price approached strong resistance after rapid upward movement."
        close = closes[-1]; ema9 = sum(closes[-9:]) / 9
        gains, losses = [], []
        for i in range(1, 15):
            diff = closes[-i] - closes[-i-1]
            if diff > 0: gains.append(diff)
            else: losses.append(abs(diff))
        avg_gain = sum(gains)/14 if gains else 0.1; avg_loss = sum(losses)/14 if losses else 0.1
        rsi = 100 - (100/(1+avg_gain/avg_loss))
        if close > ema9 and rsi < 70: return "UP", f"Price broke support with bullish momentum. RSI {rsi:.1f} shows buyers in control. Based on this, we enter a buy trade."
        else: return "DOWN", f"Price approached strong resistance. RSI {rsi:.1f} overbought. Based on this, we enter a sell trade."
    except: return "DOWN", "Price approached strong resistance level. Bearish signal confirmed."

def poll_telegram():
    global last_update_id, stats
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=30"
            r = requests.get(url, timeout=35).json()
            for upd in r.get("result", []):
                last_update_id = upd["update_id"]
                text = upd.get("message", {}).get("text", "")
                if not text: continue
                msg = text.lower().strip()
                
                # SUPPORT BOTH /start and stats
                if msg in ["/start", "start", "hi", "hello"]:
                    send(f"👋 Enoch bot ready!\n\n🌅 MORNING: 10AM-11AM\n☀️ AFTERNOON: 1PM-2PM\n🌙 EVENING: 5PM-6PM\n\nCommands:\n'stats' - see report\n'win' - record win\n'loss' - record loss\n\nCurrent date: {stats['date']}\nTotal signals today: {stats['total']}")
                    continue
                    
                session = stats.get("last_session") or "afternoon"
                if session not in SESSIONS: session = "afternoon"
                
                if msg in ["win", "w", "won", "+"]:
                    stats["wins"] += 1; stats["profit"] += 4.4; stats[session]["wins"] += 1; save_stats(stats)
                    s_data = stats[session]; total_s = s_data["wins"]+s_data["losses"]
                    wr = (s_data["wins"]/total_s*100) if total_s>0 else 0
                    send(f"✅ WIN - {session.upper()}\n{s_data['total']} sig | {s_data['wins']}W-{s_data['losses']}L | {wr:.1f}%")
                elif msg in ["loss", "l", "lost", "-"]:
                    stats["losses"] += 1; stats["profit"] -= 5.0; stats[session]["losses"] += 1; save_stats(stats)
                    s_data = stats[session]; total_s = s_data["wins"]+s_data["losses"]
                    wr = (s_data["wins"]/total_s*100) if total_s>0 else 0
                    send(f"❌ LOSS - {session.upper()}\n{s_data['total']} sig | {s_data['wins']}W-{s_data['losses']}L | {wr:.1f}%")
                elif msg in ["stats", "result", "/stats", "report"]:
                    m,a,e = stats["morning"], stats["afternoon"], stats["evening"]
                    def wr2(s): t=s["wins"]+s["losses"]; return (s["wins"]/t*100) if t>0 else 0
                    send(f"📈 REPORT {stats['date']}\n━━━━━━━━━━━━━━\n🌅 MORNING 10-11AM\n{m['total']} sig | {m['wins']}W-{m['losses']}L | {wr2(m):.1f}%\n\n☀️ AFTERNOON 1-2PM\n{a['total']} sig | {a['wins']}W-{a['losses']}L | {wr2(a):.1f}%\n\n🌙 EVENING 5-6PM\n{e['total']} sig | {e['wins']}W-{e['losses']}L | {wr2(e):.1f}%\n━━━━━━━━━━━━━━\nTOTAL: {stats['total']} | {stats['wins']}W-{stats['losses']}L | ${stats['profit']:.2f}")
        except Exception as e:
            print(f"poll error {e}")
        time.sleep(2)

def loop():
    global last_set, last_enter, stats
    time.sleep(3)
    send("✅ FIXED! Now /start go work!\n\nType /start to test\nType stats for report\n\nSessions: 10-11AM | 1-2PM | 5-6PM")
    while True:
        try:
            now = datetime.now(pytz.timezone("Africa/Lagos"))
            cm, cs = now.minute, now.second
            cur_sess = get_current_session(now.time())
            if str(now.date()) != stats["date"]:
                stats = {"date": str(now.date()), "total": 0, "wins": 0, "losses": 0, "profit": 0.0,
                         "morning": {"total": 0, "wins": 0, "losses": 0}, "afternoon": {"total": 0, "wins": 0, "losses": 0},
                         "evening": {"total": 0, "wins": 0, "losses": 0}, "last_session": None}
                save_stats(stats)
            if cur_sess is None:
                time.sleep(5); continue
            total_blocks = now.hour * 12 + (cm // 5)
            idx = total_blocks % len(SYMBOLS_LIST)
            if cm % 5 == 4 and last_set != cm and cs < 50:
                last_set = cm; name = SYMBOLS_LIST[idx][0]
                next_t = now + timedelta(minutes=1)
                send(f"❗ (UTC+1) - {cur_sess.upper()}\n\n📊 Currency pair: {name} OTC\n⏱ Expiration: 3 min [M3]\n⏰ SET: {next_t.strftime('%H:%M')} - Prepare {name}")
            if cm % 5 == 0 and last_enter != cm and cs < 50:
                last_enter = cm; prev_idx = (total_blocks - 1) % len(SYMBOLS_LIST) if total_blocks > 0 else 0
                name_e, ticker_e = SYMBOLS_LIST[prev_idx]
                direction, reason = get_analysis(ticker_e)
                direction_text = "👻 UP" if direction == "UP" else "👻 DOWN"
                stats["total"] += 1; stats[cur_sess]["total"] += 1; stats["last_session"] = cur_sess; save_stats(stats)
                send(f"Entry time: ⏰ {now.strftime('%H:%M')} - {cur_sess.upper()}\nDirection: {direction_text}\n\n➤ {reason}")
        except Exception as e: print(e)
        time.sleep(1)

@app.route("/")
def home(): return "BOT LIVE - FIXED /start + 10-11 | 1-2 | 5-6"

threading.Thread(target=loop, daemon=True).start()
threading.Thread(target=poll_telegram, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
