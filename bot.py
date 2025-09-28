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



# ◼️ IMAGE FETCHER
async def get_anime_image(rating="safe") -> bytes:
    url = f"https://caution.a0001.net/h3ntai.php?rating={rating}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"API error {resp.status}")
            data = await resp.json()

            # Extract image URL from JSON
            img_url = data.get("image", {}).get("url")
            if not img_url:
                raise Exception("No image URL found in response")

            # Fetch the actual image bytes
            async with session.get(img_url) as img_resp:
                if img_resp.status != 200:
                    raise Exception(f"Failed to fetch image {img_resp.status}")
                return await img_resp.read()


# ◼️ COMMAND HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I’m alive and ready.\n\n➡️ Use /help to see what I can do.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Commands:\n\n"
        "/start – Welcome message\n"
        "/help – Show this help menu\n"
        "/image <rating> – Get an anime image\n"
        "Available ratings: safe, suggestive, borderline, explicit\n"
        "Example: /image safe"
    )

async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rating = "safe"
    if context.args:
        rating = context.args[0].lower()

    try:
        img_data = await get_anime_image(rating)
        await update.message.reply_photo(photo=img_data, caption=f"Here’s a {rating} image!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Could not fetch image: {e}")


# Fallback for unknown commands
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
