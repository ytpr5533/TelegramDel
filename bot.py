import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Application.builder().token(BOT_TOKEN).build()

# 🔹 Delete messages after 5s (in groups)
async def delete_after_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type in ["group", "supergroup"]:
        chat_id = update.effective_chat.id
        msg_id = update.message.message_id

        # reply with warning
        warn_msg = await update.message.reply_text("⚠️ This message will be deleted in 5 sec")

        # wait 5 sec
        await asyncio.sleep(5)

        try:
            await context.bot.delete_message(chat_id, msg_id)
            await context.bot.delete_message(chat_id, warn_msg.message_id)
        except Exception as e:
            print("❌ Failed to delete:", e)

# 🔹 Show UID when forwarding to bot (in private chat)
async def show_forward_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        fwd = update.message.forward_from
        fwd_chat = update.message.forward_from_chat

        if fwd:
            await update.message.reply_text(f"👤 Forwarded User ID: `{fwd.id}`", parse_mode="Markdown")
        elif fwd_chat:
            await update.message.reply_text(f"📢 Forwarded from Channel/Group ID: `{fwd_chat.id}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("⚠️ Sorry, I can’t detect the UID (maybe privacy settings are on).")

# Handlers
app.add_handler(MessageHandler(filters.ALL & (~filters.StatusUpdate.ALL), delete_after_delay))
app.add_handler(MessageHandler(filters.FORWARDED, show_forward_uid))

if __name__ == "__main__":
    print("🤖 Bot started...")
    app.run_polling()
