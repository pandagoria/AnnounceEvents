import discord
from discord.ext import commands
import logging
import json
import sys
from TelegramBot import TGBot
from config.discord_config import DISCORD_CONFIG

logging.basicConfig(filename="botlog.txt", level=logging.DEBUG)

js: dict = {}
with open("message.json") as f:
    js = json.load(f)


# UTILS
def is_script_mode() -> bool:
    try:
        return True if sys.argv[1] == "script" else False
    except IndexError:
        return False


def publish_tg():
    TGBot(js).sendMassage()


async def publish_ds():
    channel_ids = config["channel_ids"]
    if len(js["youtube"]) > 0:
        channel = DiscordBot.get_channel(channel_ids["youtube"])
        await channel.send(js["youtube"])
    if len(js["announcement"]) > 0:
        channel = DiscordBot.get_channel(channel_ids["announcement"])
        await channel.send(js["announcement"])
    if len(js["private-chat"]) > 0:
        channel = DiscordBot.get_channel(channel_ids["private-chat"])
        await channel.send(js["private-chat"])


async def save_and_publish(key: str, msg: str):
    with open("message.json", "w") as fd:
        js[key] = msg
        logging.debug(js)
        json.dump(js, fd, indent=3)
    await publish_ds()
    publish_tg()


# BOT
config = DISCORD_CONFIG
DiscordBot = commands.Bot(
    command_prefix=config["prefix"], intents=discord.Intents().all()
)


# Если нужно только скриптом выложить, то сразу выкладываем и заканчиваем работу
# Если бот, то просто запуск, ничего не делаем
@DiscordBot.event
async def on_ready():
    if is_script_mode():
        logging.info("Запущен в скриптовом режиме")
        publish_tg()
        await publish_ds()


@DiscordBot.command()
async def STREAM(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Запись и публикация анонса")
        await save_and_publish("announcement", msg)


@DiscordBot.command()
async def YT(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Запись и публикация анонса видео на YouTube")
        await save_and_publish("youtube", msg)


@DiscordBot.command()
async def TEST(ctx, *, msg):
    check = await DiscordBot.is_owner(ctx.author)
    if isinstance(ctx.channel, discord.channel.DMChannel) and check:
        logging.info("Выолняется тестовая команда")
        await save_and_publish("private-chat", msg)


DiscordBot.run(config["token"])
