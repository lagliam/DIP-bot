# bot.py
# DIP-bot
# Author: Liam Goring

import os
from pathlib import Path

import discord
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
    app = App(bot)
    await app.run()


bot.run(TOKEN)
