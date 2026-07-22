import asyncio
import logging
import os

from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("relaybot")
logging.getLogger("telethon").setLevel(logging.WARNING)

# --- Config (set these as environment variables on Railway) ---
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
SOURCE_CHANNEL = os.environ["SOURCE_CHANNEL"]        # e.g. @patrickstarsfarm
DESTINATION_CHANNEL = os.environ["DESTINATION_CHANNEL"]  # e.g. @patricktesting

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, catch_up=True)


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def relay_new_post(event):
    try:
        await event.message.forward_to(DESTINATION_CHANNEL)
        log.info("Relayed post (id=%s) from %s to %s",
                 event.message.id, SOURCE_CHANNEL, DESTINATION_CHANNEL)
    except Exception as e:
        log.exception("Failed to relay post (id=%s): %s", event.message.id, e)


async def main():
    await client.start()
    me = await client.get_me()
    log.info("Logged in as %s (id=%s)", me.username or me.first_name, me.id)

    try:
        entity = await client.get_entity(SOURCE_CHANNEL)
        log.info("Resolved source channel '%s' -> id=%s", SOURCE_CHANNEL, entity.id)
    except Exception as e:
        log.error("Could NOT resolve source channel '%s': %s", SOURCE_CHANNEL, e)

    try:
        entity = await client.get_entity(DESTINATION_CHANNEL)
        log.info("Resolved destination channel '%s' -> id=%s", DESTINATION_CHANNEL, entity.id)
    except Exception as e:
        log.error("Could NOT resolve destination channel '%s': %s", DESTINATION_CHANNEL, e)

    log.info("Watching %s, relaying every new post to %s", SOURCE_CHANNEL, DESTINATION_CHANNEL)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
