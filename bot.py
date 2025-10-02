# from telegram import Update
# from telegram.ext import Application,CommandHandler,MessageHandler,filters,ContextTypes

# TOKEN = ""
# ADMIN_CHAT_ID = 5286630701  # Replace with your Telegram ID


from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==== CONFIG ====
BOT_A_ID = 8383101634        # Replace with Bot A's user ID
GROUP_CHAT_ID = -2391296436  # Replace with your group's chat ID
BOT_B_TOKEN = "8344957724:AAGX-cRM_-piq3u55UtMPTqOYZYFJC55q1w"  # Replace with Bot B token from BotFather

# Store mapping: user_id -> last message id in group
user_requests = {}

# ==== HANDLERS ====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey! Send me a command and I’ll get the answer for you.")

async def handle_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Send to group (with a tag so we can match later)
    sent_msg = await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"{text}\n\n[REQ_BY:{user_id}]"
    )

    # Map this group message to the user
    user_requests[sent_msg.message_id] = user_id

    await update.message.reply_text("Got it. Fetching response...")

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only watch for Bot A replies
    if update.message.from_user and update.message.from_user.id == BOT_A_ID:
        reply_text = update.message.text

        # Try to find tagged request
        if update.message.reply_to_message and update.message.reply_to_message.message_id in user_requests:
            user_id = user_requests[update.message.reply_to_message.message_id]

            # Send Bot A's reply back to the user
            await context.bot.send_message(chat_id=user_id, text=reply_text)

            # Cleanup mapping
            del user_requests[update.message.reply_to_message.message_id]

# ==== MAIN ====
def main():
    app = Application.builder().token(BOT_B_TOKEN).build()

    # Handlers for private chat with users
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_user_command))

    # Handler for group messages
    app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, handle_group_message))

    print("Bot B is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

