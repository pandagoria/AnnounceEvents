import discord
from discord.ext import commands
import logging
from TelegramBot import TGBot
from config import DISCORD_CONFIG
import requests
import asyncio

# logging.basicConfig(level=logging.INFO)


class Cmds(commands.Cog, name="cmds"):
    def __init__(self, bot) -> None:
        self.bot = bot

    async def publish(self, chat_name, ctx, msg: str):
        res = {"content": msg}
        if len(ctx.message.attachments) > 0:
            attachment = ctx.message.attachments[0]
            if (
                attachment.filename.endswith(".jpg")
                or attachment.filename.endswith(".jpeg")
                or attachment.filename.endswith(".png")
                or attachment.filename.endswith(".webp")
                or attachment.filename.endswith(".gif")
            ):
                img_data = requests.get(attachment.url).content
                with open("image_name.jpg", "wb") as handler:
                    handler.write(img_data)
                    attch = discord.File(fp="image_name.jpg", filename="image_name.jpg")
                    res["file"] = attch
                self.bot.telegram_bot.sendMessage(msg, attachment.url)
        else:
            self.bot.telegram_bot.sendMessage(msg)
        # discord
        channel_ids = self.bot.config["channel_ids"]
        if len(msg) > 0:
            channel = self.bot.get_channel(channel_ids[chat_name])
            await channel.send(**res)

    @commands.hybrid_command(name="stream", with_app_command=True)
    @commands.is_owner()
    async def stream(self, ctx, msg):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            logging.info("Запись и публикация анонса")
            await self.publish("announcement", ctx, msg)

    @commands.hybrid_command(name="test", with_app_command=True)
    @commands.is_owner()
    async def test(self, ctx, msg):
        if isinstance(ctx.channel, discord.channel.DMChannel):
            logging.info("Выолняется тестовая команда")
            await self.publish("test", ctx, msg)

    @commands.hybrid_command(name="close", with_app_command=True)
    @commands.is_owner()
    async def close(self, ctx):
        await self.close()
        print("Bot Closed")


class DiscordBot(commands.Bot):
    def __init__(
        self, config: dict, twitch_bot=None, telegram_bot=None, **kwargs
    ) -> None:
        self.config = config
        self.twitch_bot = twitch_bot
        self.telegram_bot = telegram_bot
        super().__init__(**kwargs)

    async def publish(self, chat_name, msg: str):
        # discord
        channel_ids = self.config["channel_ids"]
        if len(msg) > 0:
            channel = self.get_channel(channel_ids[chat_name])
            await channel.send(msg)
        # tg
        self.telegram_bot.sendMessage(msg)

    async def on_shutdown(self, ctx):
        await self.close()
        logging.info("Bot closed")


async def hui(ds):
    await ds.add_cog(Cmds(ds))
    await ds.start(token=config["token"], reconnect=True)


if __name__ == "__main__":
    config = DISCORD_CONFIG.copy()
    telegram_bot = TGBot()
    ds = DiscordBot(
        config=config,
        command_prefix=config["prefix"],
        intents=discord.Intents().all(),
        telegram_bot=telegram_bot,
    )
    asyncio.run(hui(ds))
