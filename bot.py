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

    # reply with warning
    warn_msg = await update.message.reply_text("⚠️ This message will be deleted in 5 sec")

    # wait 5 sec
    await asyncio.sleep(5)

    # delete both the user’s message and warning
    try:
        await context.bot.delete_message(chat_id, msg_id)
        await context.bot.delete_message(chat_id, warn_msg.message_id)
    except Exception as e:
        print("❌ Failed to delete:", e)

# apply to all user messages (ignore join/leave system messages)
app.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.ALL), delete_after_delay))

if __name__ == "__main__":
    print("🤖 Bot started...")
    app.run_polling()
