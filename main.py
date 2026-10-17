import os
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@EnochStrategyBot")

async def send_to_channel(context, text):
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=text)
    except Exception as e:
        print(f"Channel error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is LIVE! /signal will post to @EnochStrategyBot")
    await send_to_channel(context, "🚀 Enoch Strategy Bot is LIVE!\n\nTHIS IS NOT GAMBLING, THIS IS STRATEGY!")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 EURUSD STRATEGY SIGNAL\n\n🟢 BUY BIAS\nSL: 10 pips\nTP: 20 pips\n\n⏰ Evening Session 5-6PM\n\n@EnochStrategyBot"
    await update.message.reply_text("✅ Signal posted to channel!")
    await send_to_channel(context, msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📋 REPORT - @EnochStrategyBot"
    await send_to_channel(context, msg)
    await update.message.reply_text("Stats posted!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("eurusd", signal))
    app.add_handler(CommandHandler("stats", stats))
    print(f"BOT LIVE - Posting to {CHANNEL_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
