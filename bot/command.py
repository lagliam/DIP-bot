import sqlite3
import time
from pathlib import Path

import discord

import bot.database
import bot.text as text
from bot.send_image import send_image
from bot.main_loop import main_loop
from bot.motivashon import get_motivated
from bot.utility import get_seen_images, delete_seen_by_guild, log_event


async def start_posting(ctx):
    guild_id = ctx.channel.guild.id
    channel_id = ctx.channel.id
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    if Path(running_file).exists():
        Path(running_file).unlink()
        log_event(f'Stopped posting for server {guild_id}')
        await ctx.send(text.STOP_POSTING)
        return
    else:
        defaults = (f'{channel_id}', f'{guild_id}', '1', '1', f'{time.time()}', '0+-')
        conn = bot.database.sqlite_connection()
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO guilds VALUES(?,?,?,?,?,?);", defaults)
            conn.commit()
            conn.close()
        except sqlite3.Error as error:
            conn.close()
            log_event(f"Error while adding to db for guild {guild_id} {error}")
        Path(running_file).touch()
        log_event(f'Started posting for server {guild_id}')
        await ctx.send(text.START_POSTING)

    await main_loop(ctx, running_file, guild_id, channel_id)
    await ctx.send(text.START_POSTING_END)
    log_event(f'Ending posting for {guild_id}')


async def get_one(ctx):
    guild_id = ctx.channel.guild.id
    sent = await send_image(ctx, guild_id, ctx.channel.id)
    if not sent:
        await ctx.send(text.NO_MORE_TO_SEE)


async def reset_viewed(ctx):
    delete_seen_by_guild(ctx.channel.guild.id)
    await ctx.send(text.RESET_VIEWED_MESSAGE)


async def post_amount(ctx, arg):
    if not arg.isnumeric():
        await ctx.send(text.POST_AMOUNT_ERROR)
        return
    if int(arg) > 5 or int(arg) < 0 or int(arg) == 0:
        await ctx.send(text.CHANGE_FREQUENCY_ERROR)
        return
    bot.utility.set_post_amount(ctx.channel.id, arg)
    await ctx.send(text.POST_AMOUNT_END)


async def change_frequency(ctx, arg):
    if not arg.isnumeric():
        await ctx.send(text.CHANGE_FREQUENCY_ERROR)
        return
    if int(arg) > 5 or int(arg) < 0 or int(arg) == 0:
        await ctx.send(text.CHANGE_FREQUENCY_ERROR)
        return
    bot.utility.set_post_frequency(ctx.channel.id, arg)
    await ctx.send(text.CHANGE_FREQUENCY_END)


async def start_motivashon(ctx):
    await get_motivated()
    await ctx.send('', file=discord.File('../motivashon/scuff_motivation.jpg'))
    Path('../motivashon/scuff_motivation.jpg').unlink()
