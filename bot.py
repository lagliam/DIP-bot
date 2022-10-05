# bot.py
# DIP-bot
# Author: Liam Goring

import os
from datetime import datetime
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv

import bot.command as bot_command
import bot.text as text
from bot.startup import startup

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


@bot.command(name='start_posting', help=text.START_POSTING_HELP,
             brief=text.START_POSTING_BRIEF)
async def start_posting(ctx):
    await bot_command.start_posting(ctx)


@bot.command(name='!uWu!!', help=text.GET_IMAGE_HELP,
             brief=text.GET_IMAGE_BRIEF)
async def get_one(ctx):
    await bot_command.get_one(ctx)


@bot.command(name='reset_viewed', help=text.RESET_VIEWED_HELP,
             brief=text.RESET_VIEWED_BRIEF)
async def reset_viewed(ctx):
    await bot_command.reset_viewed(ctx)


@bot.command(name='post_amount', help=text.POST_AMOUNT_HELP,
             brief=text.POST_AMOUNT_BRIEF)
async def post_amount(ctx, arg):
    await bot_command.post_amount(ctx, arg)


@bot.command(name='change_frequency', help=text.CHANGE_FREQUENCY_HELP,
             brief=text.CHANGE_FREQUENCY_BRIEF)
async def change_frequency(ctx, arg):
    await bot_command.change_frequency(ctx, arg)


@bot.command(name='motivashon', help=text.START_MOTIVASHON_HELP,
             brief=text.START_MOTIVATION_BRIEF)
async def start_motivashon(ctx):
    await bot_command.start_motivashon(ctx)


@bot.event
async def on_ready():
    print(f'{datetime.now()}> Oni-chan! {bot.user.name} has connected to Discord! 0w0')
    await startup(bot)


bot.run(TOKEN)
