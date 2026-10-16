import time, random, requests
from datetime import datetime
import pytz

# === YOUR DETAILS ===
TELEGRAM_TOKEN = "8529194860:AAEIYxcxtn-AINmNsODEr-oNAVZblQ-elNU"
TELEGRAM_CHAT_ID = "8868905914"
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print("Sent:", msg)
    except Exception as e:
        print("Error:", e)

def make_signal():
    # Your EXACT fine format
    wat = pytz.timezone('Africa/Lagos')
    now = datetime.now(wat).strftime("%H:%M")
    
    pair = "EUR/USD"
    side = random.choice(["BUY 🟢", "SELL 🔴"])
    
    if "BUY" in side:
        direction = "🐻 DOWN" if random.random() < 0.5 else "🐂 UP"
        # Keep it EUR/USD
        direction = "🐂 UP" if "BUY" in side else "🐻 DOWN"
        if "BUY" in side:
            direction_text = "🐂 UP"
        else:
            direction_text = "🐻 DOWN"
    else:
        direction_text = "🐻 DOWN"

    # Your format from yesterday:
    msg = f"""📊Currency pair: {pair}
Direction: {direction_text}

🔥 {pair} - {side}
⏰ Time: {now} (UTC+1)
⏳ Expiry: 1 Min
📊 Reason: Strong trend

👉 Trade here: {POCKET_LINK}

⚠️ Risk: 1-2% only"""
    return msg

send_telegram("✅ Enoch Bot V3 don start! EUR/USD signals every 1 min go dey enter now. Format don set!")

while True:
    sig = make_signal()
    send_telegram(sig)
    time.sleep(60)  # 1 min
