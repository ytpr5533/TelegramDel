import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Bot token from Railway environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(BOT_TOKEN).build()

# delete every message after 5 seconds
async def delete_after_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    await asyncio.sleep(5)  # wait 5 sec
    try:
        await context.bot.delete_message(chat_id, msg_id)
    except Exception as e:
        print("❌ Failed to delete:", e)

app.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.ALL), delete_after_delay))

if __name__ == "__main__":
    print("🤖 Bot started...")
    app.run_polling()
