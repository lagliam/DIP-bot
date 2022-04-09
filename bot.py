# bot.py
# DIP-bot
# Author: Liam Goring Nov 2021

from datetime import datetime
import os
from pathlib import Path
import discord
import time

from discord.ext import commands
from dotenv import load_dotenv

from bot.main_loop import main_loop
from bot.startup import check_running
from bot.get_image import send_image
from bot.utility import file_to_array, delete_seen_by_guild
import bot.text as text
from bot.motivashon import get_motivated

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='start_posting', help=text.START_POSTING_HELP,
             brief=text.START_POSTING_BRIEF)
async def start_posting(ctx):
    guild_id = ctx.channel.guild.id
    channel_id = ctx.channel.id
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    if os.path.exists(running_file):
        os.remove(running_file)
        await ctx.send(text.STOP_POSTING)
        return
    else:
        with open(running_file, 'a+') as fp:
            fp.write('post_amount 1\n')
            fp.write('post_frequency 1\n')
            fp.write(f'last_post {time.time()}\n')
            fp.write('all_seen false\n')

    print(f'started posting for server {guild_id}')
    await ctx.send(text.START_POSTING)

    await main_loop(ctx, running_file, guild_id, channel_id)

    await ctx.send(text.START_POSTING_END)
    print(f'{datetime.now()}> Ending posting for {guild_id}')


@bot.command(name='!uWu!!', help=text.GET_IMAGE_HELP,
             brief=text.GET_IMAGE_BRIEF)
async def get_one(ctx):
    guild_id = ctx.channel.guild.id
    sent = await send_image(
        ctx, file_to_array(f'../guilds/images_{guild_id}.txt'), guild_id)
    if not sent:
        await ctx.send('(o･｀Д´･o) Baka! No more images to see')


@bot.command(name='reset_viewed', help=text.RESET_VIEWED_HELP,
             brief=text.RESET_VIEWED_BRIEF)
async def reset_viewed(ctx):
    delete_seen_by_guild(ctx.channel.guild.id)
    await ctx.send(text.RESET_VIEWED_MESSAGE)


@bot.command(name='post_amount', help=text.POST_AMOUNT_HELP,
             brief=text.POST_AMOUNT_BRIEF)
async def post_amount(ctx, arg):
    if not arg.isnumeric():
        await ctx.send(text.POST_AMOUNT_ERROR)
        return
    guild_id = ctx.channel.guild.id
    channel_id = ctx.channel.id
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    new_file = ""
    with open(running_file, 'r') as fp:
        for line in fp:
            key, value = line.split()
            if int(value) > 5 or int(value) < 0 or int(value) == 0:
                await ctx.send(text.POST_AMOUNT_ERROR)
                return
            if key == 'post_amount':
                line = f'post_amount {arg}\n'
            new_file += line
    write_file = open(f'../guilds/{guild_id}.{channel_id}.running', 'w')
    write_file.writelines(new_file)
    write_file.close()
    await ctx.send(text.POST_AMOUNT_END)


@bot.command(name='change_frequency', help=text.CHANGE_FREQUENCY_HELP,
             brief=text.CHANGE_FREQUENCY_BRIEF)
async def change_frequency(ctx, arg):
    if not arg.isnumeric():
        await ctx.send(text.CHANGE_FREQUENCY_ERROR)
        return
    guild_id = ctx.channel.guild.id
    channel_id = ctx.channel.id
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    new_file = ""
    with open(running_file, 'r') as fp:
        for line in fp:
            key, value = line.split()
            if int(value) > 5 or int(value) < 0 or int(value) == 0:
                await ctx.send(text.CHANGE_FREQUENCY_ERROR)
                return
            if key == 'post_frequency':
                line = f'post_frequency {arg}\n'
            new_file += line
    write_file = open(f'../guilds/{guild_id}.{channel_id}.running', 'w')
    write_file.writelines(new_file)
    write_file.close()
    await ctx.send(text.CHANGE_FREQUENCY_END)


@bot.command(name='motivashon', help=text.START_MOTIVASHON_HELP,
             brief=text.START_MOTIVATION_BRIEF)
async def start_motivashon(ctx):
    await get_motivated()
    await ctx.send('', file=discord.File('../motivashon/scuff_motivation.jpg'))
    os.remove('../motivashon/scuff_motivation.jpg')


@bot.event
async def on_ready():
    print(f'{datetime.now()}> Oni-chan! {bot.user.name} has connected to Discord! 0w0')
    await check_running(bot)


bot.run(TOKEN)
