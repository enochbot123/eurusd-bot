import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REGISTER_LINK = "https://pocketoption.com"
ADMIN_USERNAME = "@Enochsystem"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER WITH POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("📊 Start Signals", callback_data='start_signals')],
        [InlineKeyboardButton("🆔 My Trading ID", callback_data='my_id'),
         InlineKeyboardButton("ℹ️ How it works", callback_data='how')]
    ])

WELCOME = """⭐ ENOCH PROFESSIONAL TRADING SYSTEM ⭐

Hello {name} 👋

📊 HOW TO GET YOUR TRADING ID:
1️⃣ Click REGISTER button below
2️⃣ Register & fund $10
3️⃣ Copy Trader ID
4️⃣ Paste ID here for this bot

👇 Click below:
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME.format(name=update.effective_user.first_name), reply_markup=main_menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == 'my_id':
        await q.edit_message_text("🆔 Send your Trader ID here\n\nExample: 12345678\nJust type am and send!", reply_markup=main_menu())
    elif q.data == 'how':
        await q.edit_message_text(f"ℹ️ 1. Register\n2. Send ID here\n3. Get VIP signals\n\nHelp: {ADMIN_USERNAME}", reply_markup=main_menu())
    else:
        await q.edit_message_text("✅ To start, send your Trading ID first!", reply_markup=main_menu())

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader_id = update.message.text
    print(f"NEW ID: {update.effective_user.first_name} ({update.effective_user.id}) => {trader_id}")
    await update.message.reply_text(
        f"✅ Received!\n\nTrader ID: {trader_id}\nI don forward to admin. You go get VIP soon!\nKeep your username open!",
        reply_markup=main_menu()
    )

async def post_init(app: Application):
    # THIS GO KILL THE CONFLICT ERROR!
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted - Conflict fixed!")

def main():
    print("Bot started - Private Reply Mode ON")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
