from telethon import TelegramClient, events, types
import logging
import asyncio

# ================= CONFIG =================
API_ID = 28980184                 # Your Telegram API ID
API_HASH = "087803ce7bd17d500ea9e223db2af018"       # Your Telegram API Hash
SESSION_NAME = "userbot_session" # Session file name
GROUP_USERNAME = "t.me/informationtool"  # e.g., t.me/YourGroupUsername
BOT_A_ID = 8200107278             # Bot A's user ID

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= TELETHON CLIENT =================
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Store mapping: message_id in group -> user_id
user_requests = {}

# ================= HANDLERS =================
@client.on(events.NewMessage)
async def handle_user_dm(event):
    """Handle commands sent by users to userbot."""
    try:
        if not event.is_private:
            return  # only process private messages

        user_id = event.sender_id
        text = event.raw_text

        # 1️⃣ Check if user is in the group
        try:
            member = await client.get_participant(GROUP_USERNAME, user_id)
        except Exception:
            # user not in group
            await event.reply(f"❌ You must join our group first:\nhttps://t.me/{GROUP_USERNAME}")
            return

        # 2️⃣ Forward command to Bot A in the group
        group_msg = await client.send_message(GROUP_USERNAME, f"{text}")
        user_requests[group_msg.id] = user_id
        await event.reply("✅ Request sent! Waiting for Bot A response...")

    except Exception as e:
        logger.error(f"Error handling user DM: {e}")
        await event.reply("⚠️ Something went wrong.")

@client.on(events.NewMessage)
async def handle_group_messages(event):
    """Catch replies from Bot A in the group."""
    try:
        if event.chat.username != GROUP_USERNAME:
            return  # ignore other chats

        if event.sender_id != BOT_A_ID:
            return  # only process messages from Bot A

        # Make sure this is a reply to one of our forwarded messages
        if event.is_reply:
            replied_id = event.reply_to_msg_id
            if replied_id in user_requests:
                user_id = user_requests[replied_id]
                await client.send_message(user_id, f"{event.raw_text}")
                logger.info(f"Delivered Bot A reply to user {user_id}")
                del user_requests[replied_id]

    except Exception as e:
        logger.error(f"Error handling group message: {e}")

# ================= MAIN =================
async def main():
    await client.start()
    logger.info("Userbot started. Listening for messages...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
