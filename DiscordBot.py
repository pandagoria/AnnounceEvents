import discord
from discord.ext import commands
import logging
from TelegramBot import TGBot
from config.discord_config import DISCORD_CONFIG

logging.basicConfig(filename="botlog.txt", level=logging.DEBUG)


# UTILS
telegram_bot = TGBot()


async def publish_ds(chat_name, msg: str):
    channel_ids = config["channel_ids"]
    if len(msg) > 0:
        channel = DiscordBot.get_channel(channel_ids[chat_name])
        await channel.send(msg)


# BOT
config = DISCORD_CONFIG
DiscordBot = commands.Bot(
    command_prefix=config["prefix"], intents=discord.Intents().all()
)


@DiscordBot.command()
async def STREAM(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Запись и публикация анонса")
        await publish_ds("announcement", msg)
        telegram_bot.sendMessage(msg)


@DiscordBot.command()
async def YT(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Запись и публикация анонса видео на YouTube")
        await publish_ds("youtube", msg)
        telegram_bot.sendMessage(msg)


@DiscordBot.command()
async def TEST(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Выолняется тестовая команда")
        await publish_ds("test", msg)
        telegram_bot.sendMessage(msg)


DiscordBot.run(config["token"])
