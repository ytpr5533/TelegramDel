import aiohttp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

TOKEN = "8344957724:AAGX-cRM_-piq3u55UtMPTqOYZYFJC55q1w"
ADMIN_CHAT_ID = 5286630701  # Replace with your Telegram ID


# ◼️ IMAGE URL FETCHER (returns raw text)
async def get_anime_image_url(rating="safe") -> str:
    url = f"https://caution.a0001.net/h3ntai.php?rating={rating}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()   # return raw text instead of parsing JSON


# ◼️ COMMAND HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I’m alive and ready.\n\n➡️ Use /help to see what I can do.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Commands:\n\n"
        "/start – Welcome message\n"
        "/help – Show this help menu\n"
        "/image <rating> – Get an anime image link\n"
        "Available ratings: safe, suggestive, borderline, explicit\n"
        "Example: /image explicit"
    )

async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rating = "safe"
    if context.args:
        rating = context.args[0].lower()

    try:
        img_url = await get_anime_image_url(rating)
        await update.message.reply_text(f"🔗 Here’s a {rating} image URL:\n{img_url}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch image URL: {e}")


# Unknown commands
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Try /help")


# ◼️ STARTUP
async def on_startup(app: Application):
    print("✅ Bot is live!")
    try:
        await app.bot.send_message(chat_id=ADMIN_CHAT_ID, text="🤖 Bot is live and ready!")
    except Exception as e:
        print(f"Startup message failed: {e}")


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(on_startup)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("image", send_image))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
