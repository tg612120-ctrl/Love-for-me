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
SOURCE_CHANNEL = os.environ["SOURCE_CHANNEL"]            # e.g. @patrickstarsfarm
DESTINATION_CHANNEL = os.environ["DESTINATION_CHANNEL"]  # e.g. @patricktesting

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH, catch_up=True)


async def main():
    await client.start()
    me = await client.get_me()
    log.info("Logged in as %s (id=%s)", me.username or me.first_name, me.id)

    # Resolve entities BEFORE registering the handler, so the filter
    # uses the actual entity instead of a raw username string.
    source_entity = await client.get_entity(SOURCE_CHANNEL)
    dest_entity = await client.get_entity(DESTINATION_CHANNEL)
    log.info("Resolved source channel '%s' -> id=%s", SOURCE_CHANNEL, source_entity.id)
    log.info("Resolved destination channel '%s' -> id=%s", DESTINATION_CHANNEL, dest_entity.id)

    @client.on(events.NewMessage(chats=source_entity))
    async def relay_new_post(event):
        log.info("Event received: id=%s", event.message.id)
        for attempt in range(3):
            try:
                await event.message.forward_to(dest_entity)
                log.info("Relayed post (id=%s) -> %s", event.message.id, DESTINATION_CHANNEL)
                break
            except Exception as e:
                log.exception("Attempt %d failed for post id=%s: %s", attempt + 1, event.message.id, e)
                await asyncio.sleep(2)

    log.info("Watching %s, relaying every new post to %s", SOURCE_CHANNEL, DESTINATION_CHANNEL)
    await client.run_until_disconnected()


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            log.exception("Bot crashed, restarting in 5s: %s", e)
            import time
            time.sleep(5)
