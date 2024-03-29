import asyncio
import os
from pathlib import Path
from typing import Dict

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from app.app import App
from app.utilities import database
from app.utilities.utility import log_event, get_cogs

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot()

command_list = get_cogs()

for cog in command_list:
    bot.load_extension(f'app.cogs.{cog}')


@bot.event
async def on_ready() -> None:
    """
    Logs when the bot is ready
    """

    log_event(f'Hello! {bot.user.name} has connected to Discord! 0w0')


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
    """
    Listens for reactions on posts to save liked amount

    :param payload: The payload object
    :type payload: discord.RawReactionActionEvent
    """

    parameters = await extract_parameters(payload)
    if parameters:
        database.add_liked_image(parameters)


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
    """
    Listens for reactions on posts to decrement liked amount

    :param payload: The payload object
    :type payload: discord.RawReactionActionEvent
    """

    parameters = await extract_parameters(payload)
    if parameters:
        database.remove_liked_image(parameters)


async def extract_parameters(payload: discord.RawReactionActionEvent) -> dict[str, int | None | str] | None:
    """Extracts the payload variables into a parameters array

    :param payload: The payload to extract parameters from
    :type payload: dict
    :returns: None
    """

    guild_id = payload.guild_id
    channel_id = payload.channel_id
    partial_messageable = bot.get_partial_messageable(channel_id)
    message_id = payload.message_id
    message = await partial_messageable.fetch_message(message_id)
    if message.author.name != bot.user.name:
        return None
    filename = message.attachments[0].filename
    parameters = {'filename': filename, 'guild_id': guild_id, 'channel_id': channel_id}
    return parameters


@tasks.loop(count=1)
async def primary_application_loop() -> None:
    """The primary application loop to run the scheduled image sender"""

    while not bot.is_ready():
        await asyncio.sleep(0.1)
    app = App(bot)
    await app.run()
    log_event('----Primary Application Loop Stopped----')


primary_application_loop.start()
bot.run(TOKEN)
