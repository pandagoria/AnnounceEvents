import asyncio
from discord import Intents
from Twitch import TwitchClient
from DiscordBot import DiscordBot, Cmds
from TelegramBot import TGBot
from config import DISCORD_CONFIG
import logging

# from queue import Queue

# from aiohttp_oauth2 import oauth2_app

# app = web.Application()

# app.add_subapp("/twitch", oauth2_app()
logging.basicConfig(level=logging.INFO, filename="NEW_LOG.txt")


async def main() -> None:
    twitch = TwitchClient()  # always first
    tg = TGBot()
    ds_conf = DISCORD_CONFIG.copy()
    ds = DiscordBot(
        config=ds_conf,
        command_prefix=ds_conf["prefix"],
        intents=Intents().all(),
        telegram_bot=tg,
    )
    twitch.discord_bot = ds
    ds.twitch_bot = twitch
    await ds.add_cog(Cmds(ds))
    await asyncio.gather(
        ds.start(token=ds_conf["token"], reconnect=True), twitch.websocket_session()
    )


# session = asyncio.run([ds.start()])

if __name__ == "__main__":
    asyncio.run(main())
