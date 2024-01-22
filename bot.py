# bot.py
# DIP-bot
# Author: Liam Goring

import os
from pathlib import Path

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from app.app import App
from app.utilities.utility import log_event, get_cogs

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot()

command_list = get_cogs()

for cog in command_list:
    bot.load_extension(f'app.cogs.{cog}')


@bot.event
async def on_ready():
    log_event(f'Hello! {bot.user.name} has connected to Discord! 0w0')


@tasks.loop(count=1)
async def primary_application_loop():
    await bot.wait_until_ready()
    app = App(bot)
    await app.run()


primary_application_loop.start()
bot.run(TOKEN)
