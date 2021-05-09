# bot.py
# DIP-bot
# Author: Liam Goring Apr 2021

import os
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

from bot.main_loop import main_loop
from bot.startup import check_running

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='uWu')
async def start_posting(ctx):
    guild_id = ctx.channel.guild.id
    channel_id = ctx.channel.id
    running_file = f'guilds/{guild_id}.{channel_id}.running'
    if os.path.exists(running_file):
        os.remove(running_file)
        return
    else:
        open(running_file, 'a').close()

    print(f'started posting for server {guild_id}')
    await ctx.send('AraAra~ Here some pics for you')

    await main_loop(ctx, running_file, guild_id)

    await ctx.send('(o･｀Д´･o) Baka!')
    print(f'Ending posting for {guild_id}')


@bot.event
async def on_ready():
    print(f'Onii-chan! {bot.user.name} has connected to Discord! 0w0')
    await check_running(bot)


bot.run(TOKEN)
