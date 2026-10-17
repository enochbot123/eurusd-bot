import os
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # e.g @EnochSignals or -10012345

async def send_to_channel(context, text):
    if CHANNEL_ID:
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
        except Exception as e:
            print(f"Channel error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Live! Use /signal to post to channel")
    await send_to_channel(context, "🚀 Bot is Live! Evening session ready!")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 EURUSD SIGNAL\n\nBUY NOW\nSL: 10 pips\nTP: 20 pips\n\nTime: Evening 5-6PM Session"
    await update.message.reply_text(f"Sent to channel:\n{msg}")
    await send_to_channel(context, msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 REPORT 2026-10-17\n\n🌙 EVENING 5-6PM\n12 sig | 0W-0L\n\nTOTAL: 12"
    await update.message.reply_text("Stats posted to channel")
    await send_to_channel(context, msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("eurusd", signal))
    print("BOT LIVE - Channel connected")
    app.run_polling()

if __name__ == "__main__":
    main()
