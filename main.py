import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
REGISTER_LINK = "https://pocketoption.com"
ADMIN_USERNAME = "@Enochsystem"
CHANNEL_USERNAME = "@EnochSignals"

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 REGISTER WITH POCKET OPTION", url=REGISTER_LINK)],
        [InlineKeyboardButton("📊 Start Signals", callback_data='start_signals')],
        [InlineKeyboardButton("🆔 My Trading ID", callback_data='my_id'),
         InlineKeyboardButton("ℹ️ How it works", callback_data='how')]
    ])

# YOUR PROFESSIONAL SETTINGS INSIDE HERE NOW!
WELCOME = """⭐ ENOCH PROFESSIONAL TRADING SYSTEM ⭐

⚠️ THIS IS NOT GAMBLING - THIS IS STRATEGY

Hello {name} 👋

📊 PROFESSIONAL SETTINGS:
📅 Sessions: 9:30AM | 2:30PM | 8:30PM WAT
⏱️ Expiry: 3 MIN [M3] | Entry M1
🧠 Strategy: Breakout + Retest + Volume
💰 Risk: 1% | Martingale 1 Step Only
🎯 Pairs: EUR/USD, GBP/USD, GOLD etc

📢 Channel: {channel}
👨‍💼 Support: {admin}

CHART SETUP:
- Resistance/Support breakout
- Volume confirmation
- Confidence 87-96%

⚠️ RISK WARNING: Trading involves risk.

👇 Choose option below to get your Trading ID:
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME.format(name=update.effective_user.first_name, channel=CHANNEL_USERNAME, admin=ADMIN_USERNAME),
        reply_markup=main_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == 'my_id':
        await q.edit_message_text(
            "🆔 HOW TO GET TRADING ID\n\n1. Click REGISTER\n2. Fund $10\n3. Copy Trader ID\n4. Paste ID here in DM\n\nExample: 12345678",
            reply_markup=main_menu()
        )
    elif q.data == 'how':
        await q.edit_message_text(f"ℹ️ 1. Register\n2. Send ID here\n3. Get VIP signals\n\nHelp: {ADMIN_USERNAME}", reply_markup=main_menu())
    else:
        await q.edit_message_text("✅ To start signals, send your Trading ID first!", reply_markup=main_menu())

async def handle_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trader_id = update.message.text
    print(f"NEW ID: {update.effective_user.first_name} ({update.effective_user.id}) => {trader_id}")
    await update.message.reply_text(
        f"✅ Received!\nTrader ID: {trader_id}\nI don forward to admin!",
        reply_markup=main_menu()
    )

async def post_init(app: Application):
    await app.bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook deleted - Conflict fixed!")

def main():
    print("Bot started - Professional Mode ON")
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
