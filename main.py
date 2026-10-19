import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
# PUT YOUR REAL POCKET OPTION LINK HERE
REGISTER_LINK = "https://pocketoption.com"
# PUT YOUR OWN USERNAME OR YOUR ADMIN ID HERE
ADMIN_USERNAME = "@Enochsystem"  # Your username

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER WITH POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("📊 Start Signals", callback_data='start_signals')],
        [InlineKeyboardButton("🆔 My Trading ID", callback_data='my_id'),
         InlineKeyboardButton("ℹ️ How it works", callback_data='how')]
    ])

WELCOME_TEXT = """
⭐ ENOCH PROFESSIONAL TRADING SYSTEM ⭐

⚠️ THIS IS NOT GAMBLING - THIS IS STRATEGY

Hello {name} 👋
Welcome!

📊 HOW TO GET YOUR TRADING ID:

1️⃣ Click REGISTER WITH POCKET OPTION button below
2️⃣ Register and fund $10 minimum
3️⃣ Copy your Trader ID from Pocket Option
4️⃣ Come back here and SEND THE ID to this bot

After you send ID, I go verify you and add you to VIP signals!

👇 Click below to start:
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        WELCOME_TEXT.format(name=name),
        reply_markup=main_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    
    if q.data == 'my_id':
        await q.edit_message_text(
            text="🆔 HOW TO GET YOUR TRADING ID\n\n"
                 "1. Click REGISTER WITH POCKET OPTION\n"
                 "2. Register account\n"
                 "3. Go to Profile -> Copy your ID (numbers)\n"
                 "4. Paste the ID here for this bot\n\n"
                 "Example: 12345678\n\n"
                 "👉 Just type the ID now and send!",
            reply_markup=main_menu()
        )
    elif q.data == 'how':
        await q.edit_message_text(
            text="ℹ️ HOW IT WORKS\n\n"
                 "1. Register with Pocket Option\n"
                 "2. Send your Trader ID here\n"
                 "3. I go verify you\n"
                 "4. You go get access to 9:30AM, 2:30PM, 8:30PM signals\n\n"
                 "Need help? Contact " + ADMIN_USERNAME,
            reply_markup=main_menu()
        )
    elif q.data == 'start_signals':
        await q.edit_message_text(
            text="✅ To start signals, you must send your Trading ID first!\n\n"
                 "Have you registered? If yes, just type your ID and send here.",
            reply_markup=main_menu()
        )

# THIS NA THE MAIN THING YOU WANT - BOT DEY REPLY PRIVATE MESSAGE
async def handle_private_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    trader_id = update.message.text

    # Reply to the user for private DM
    await update.message.reply_text(
        f"✅ Received! Thank you {user_name}\n\n"
        f"Your Trader ID: {trader_id}\n\n"
        f"I don forward am to admin. You go get confirmation soon for VIP!\n\n"
        f"Keep your Telegram username open so {ADMIN_USERNAME} fit message you.",
        reply_markup=main_menu()
    )
    
    # Forward to you (admin) - You go see am for your private bot logs or you fit add ADMIN_CHAT_ID later
    print(f"NEW ID RECEIVED: User {user_name} ({user_id}) sent ID: {trader_id}")

def main():
    print("Bot started - Private Reply Mode ON")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    # This handler makes bot reply when person sends ID for private chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_private_id))
    app.run_polling()

if __name__ == "__main__":
    main()
