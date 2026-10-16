import os, time, random, requests, pytz
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home():
    return "Enoch Bot LIVE AUD/USD"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
Thread(target=run_flask, daemon=True).start()

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
POCKET = os.environ.get("POCKET_LINK", "https://pocket-friends.co/r/8vcvh8wte5")

PAIRS = [("EUR/USD",""), ("AUD/USD",""), ("USD/JPY",""), ("GOLD","")]

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

print("Bot Started AUD/USD")
idx=0
tz=pytz.timezone("Africa/Lagos")
while True:
    try:
        pair=PAIRS[idx][0]
        act=random.choice(["BUY","SELL"])
        emoji="🟢" if act=="BUY" else "🔴"
        now=datetime.now(tz)
        ent=now+timedelta(minutes=1)
        exp=ent+timedelta(minutes=5)

        price=0.65555 if "AUD" in pair else 1.12 if "EUR" in pair else 158.2 if "JPY" in pair else 2680.0

        m1=f"⚠️ SET TIME NOW - 1 MIN LEFT!\n\nPair: {pair}\nSignal: {emoji} {act}\nPrice: {price}\n\nEntry in 1 min: {ent.strftime('%H:%M:%S')}"
        send(m1)
        print("WARNING sent")
        time.sleep(60)

        m2=f"🚀 ENTER NOW!!! {emoji} {act} {pair}\nPrice: {price}\nTime: {ent.strftime('%H:%M:%S')} NOW!\nExpiry: {exp.strftime('%H:%M:%S')}\nTrade: {POCKET}\nNext: {PAIRS[(idx+1)%4][0]}"
        send(m2)
        print("ENTER NOW sent")
        idx=(idx+1)%len(PAIRS)
        time.sleep(240)
    except Exception as e:
        print(e)
        time.sleep(30)
