# bot.py
# DIP-bot
# Author: Liam Goring Apr 2021

import os
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

from bot.main_loop import main_loop
from bot.startup import check_running
from bot.get_image import send_image
from bot.utility import file_to_array, delete_seen_by_guild

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='start_posting')
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


@bot.command(name='!uWu!!')
async def get_one(ctx):
    guild_id = ctx.channel.guild.id
    await send_image(
        ctx, file_to_array(f'guilds/images_{guild_id}.txt'), guild_id)


@bot.command(name='reset_viewed')
async def reset_viewed(ctx):
    delete_seen_by_guild(ctx.channel.guild.id)


@bot.event
async def on_ready():
    print(f'Onii-chan! {bot.user.name} has connected to Discord! 0w0')
    await check_running(bot)


bot.run(TOKEN)
