# main_loop.py
# main logic for sending images on an interval

import asyncio
import os
import random

import discord

from bot.constants import LIMIT_SIZE
from bot.constants import RUNNING_FILE_POLL_INTERVAL
from bot.constants import TRIGGER_DURATION


async def main_loop(ctx, running_file, guild_id, restart=False):
    # await ctx.send('(o･｀Д´･o) Baka!')
    counter = 0
    seen_images = file_to_array(f'../guilds/images_{guild_id}.txt')

    while counter < (len(image_list()) - len(seen_images)) and os.path.exists(
            running_file):
        file_list = image_list()
        counter += 1
        filename = file_list.pop(random.randrange(len(file_list)))
        if os.path.getsize('../images/' + filename) > LIMIT_SIZE:
            filename = file_list.pop(random.randrange(len(file_list)))
        while filename in seen_images:
            filename = file_list.pop(random.randrange(len(file_list)))
        if not restart:
            await ctx.send('', file=discord.File('../images/' + filename))
            write_viewed_image_list_for_guild(filename, guild_id)
        start_waiting = 0
        restart = False
        while start_waiting < TRIGGER_DURATION and os.path.exists(
                running_file):
            await asyncio.sleep(RUNNING_FILE_POLL_INTERVAL)
            start_waiting += RUNNING_FILE_POLL_INTERVAL


def image_list():
    directory = '../images/'
    images = []
    for filename in os.listdir(directory):
        if (filename.lower().endswith(".jpg")
                or filename.lower().endswith(".png")
                or filename.lower().endswith(".gif")
                or filename.lower().endswith(".jpeg")):
            images.append(filename)
            continue
        else:
            continue
    return images


def write_viewed_image_list_for_guild(filename, guild_id=None):
    with open(f'../guilds/images_{guild_id}.txt', 'a+') as f:
        f.write("%s\n" % filename)


def file_to_array(filename):
    array = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            array = f.readlines()
    return array
