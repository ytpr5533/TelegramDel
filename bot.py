import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)


# ==== CONFIG ====
BOT_A_ID = 8383101634        # Replace with Bot A's user ID
GROUP_CHAT_ID = -1002391296436  # Replace with your group's chat ID
BOT_B_TOKEN = "7589787815:AAEmy9yQzBKKaMMRxmV3K2CnZST1jTF4IKs"  # Replace with Bot B token from BotFather



# Track mapping: group_message_id -> user_id
user_requests = {}

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== HANDLERS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command for private chat users."""
    try:
        await update.message.reply_text(
            "Hi! Send me a command (like /price BTC) and I’ll fetch the result for you."
        )
    except Exception as e:
        logger.error(f"Error in /start: {e}")


async def handle_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user commands in private chat."""
    try:
        user_id = update.effective_user.id
        text = update.message.text

        # Forward message to group with hidden tag
        sent_msg = await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{text}\n\n[REQ_BY:{user_id}]"
        )

        # Save mapping
        user_requests[sent_msg.message_id] = user_id

        await update.message.reply_text("✅ Request received, waiting for response...")
        logger.info(f"Forwarded request from user {user_id} to group.")

    except Exception as e:
        logger.error(f"Error in handle_user_command: {e}")
        await update.message.reply_text("⚠️ Something went wrong while sending your request.")


async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle messages inside the group, capture Bot A replies."""
    try:
        # Only process Bot A messages
        if update.message.from_user and update.message.from_user.id == BOT_A_ID:
            reply_text = update.message.text or "<no text>"

            # Make sure this reply is to a tracked request
            if update.message.reply_to_message:
                original_id = update.message.reply_to_message.message_id
                if original_id in user_requests:
                    user_id = user_requests[original_id]

                    # Send back to user
                    await context.bot.send_message(chat_id=user_id, text=reply_text)
                    logger.info(f"Delivered Bot A reply to user {user_id}")

                    # Cleanup mapping
                    del user_requests[original_id]
    except Exception as e:
        logger.error(f"Error in handle_group_message: {e}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Global error handler."""
    logger.error(msg="Exception while handling update:", exc_info=context.error)

# ===================== MAIN =====================
def main():
    """Run the bot."""
    try:
        app = Application.builder().token(BOT_B_TOKEN).build()

        # Private chat handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT, handle_user_command))

        # Group message handler
        app.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, handle_group_message))

        # Error handler
        app.add_error_handler(error_handler)

        logger.info("Bot B is running...")
        app.run_polling()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

# ===================== ENTRY =====================
if __name__ == "__main__":
    main()
