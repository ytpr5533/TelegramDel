import sys
import types

# Dummy imghdr module (only for Telethon)
imghdr = types.ModuleType("imghdr")
imghdr.what = lambda *a, **k: None
sys.modules["imghdr"] = imghdr

from telethon import TelegramClient, events, types

import asyncio
import logging
from telethon import TelegramClient, events

# ================= CONFIG =================
API_ID =                     # Your Telegram API ID
API_HASH = ""  # Your Telegram API Hash
SESSION_NAME = "userbot_session"      # Session file name
GROUP_USERNAME = ""    # without t.me/
BOT_A_ID =               # Bot A's user ID

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ================= TELETHON CLIENT =================
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# Map group message IDs to original user IDs
user_requests = {}

# ================= FUNCTIONS =================
async def is_user_in_group(user_id: int) -> bool:
    """Check if a user is a member of the specified group."""
    try:
        await client.get_participant(GROUP_USERNAME, user_id)
        return True
    except Exception:
        return False

async def forward_to_bot_a(text: str) -> int | None:
    """Send a message to the group for Bot A and return the message ID."""
    try:
        msg = await client.send_message(GROUP_USERNAME, text)
        return msg.id
    except Exception as e:
        logger.error(f"Failed to forward message to group: {e}")
        return None

async def notify_user_not_in_group(event, group_username):
    """Notify the user they must join the group first."""
    try:
        await event.reply(
            f"❌ You must join our group first:\nhttps://t.me/{group_username}"
        )
    except Exception as e:
        logger.error(f"Failed to notify user about group membership: {e}")

# ================= EVENT HANDLERS =================
@client.on(events.NewMessage)
async def handle_user_dm(event):
    """Handle private messages from users."""
    if not event.is_private:
        return

    user_id = event.sender_id
    text = event.raw_text.strip()

    if not text:
        await event.reply("⚠️ Empty message received. Please send a valid command.")
        return

    try:
        if not await is_user_in_group(user_id):
            await notify_user_not_in_group(event, GROUP_USERNAME)
            return

        msg_id = await forward_to_bot_a(text)
        if msg_id:
            user_requests[msg_id] = user_id
            await event.reply("✅ Request sent! Waiting for Bot A response...")
        else:
            await event.reply("⚠️ Failed to send request to Bot A.")

    except Exception as e:
        logger.error(f"Error handling user DM: {e}")
        await event.reply("⚠️ Something went wrong while processing your message.")

@client.on(events.NewMessage)
async def handle_group_messages(event):
    """Handle messages from Bot A in the group."""
    if event.chat.username != GROUP_USERNAME:
        return  # Ignore other chats
    if event.sender_id != BOT_A_ID:
        return  # Only process Bot A messages

    if not event.is_reply:
        return  # Only handle replies

    replied_id = event.reply_to_msg_id
    if replied_id not in user_requests:
        return  # Not a tracked message

    user_id = user_requests[replied_id]
    try:
        await client.send_message(user_id, event.raw_text)
        logger.info(f"Delivered Bot A reply to user {user_id}")
        del user_requests[replied_id]
    except Exception as e:
        logger.error(f"Failed to deliver Bot A reply to user {user_id}: {e}")

# ================= HEARTBEAT =================
async def heartbeat():
    """Periodic log to indicate bot is running."""
    while True:
        logger.info("💡 Userbot is alive and running...")
        await asyncio.sleep(30)  # every 30 seconds

# ================= MAIN =================
async def main():
    try:
        await client.start()
        logger.info("✅ Userbot started. Listening for messages...")
        asyncio.create_task(heartbeat())
        await client.run_until_disconnected()
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}")

if __name__ == "__main__":
    asyncio.run(main())
