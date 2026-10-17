import os
from telegram.ext import Application, CommandHandler
TOKEN = os.getenv("BOT_TOKEN", "8529194860:AAHm527qPw0etrvMP-E7fzsce8aTZm80CyQ")
async def start(update, context):
    await update.message.reply_text("✅ BOT LIVE! E don work!")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("BOT LIVE OK")
app.run_polling()
