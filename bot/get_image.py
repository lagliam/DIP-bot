import os
import random
import discord

from bot.constants import LIMIT_SIZE
from bot.utility import image_list, write_viewed_image_list_for_guild


async def send_image(ctx, seen_images, guild_id, restart=False):
    file_list = image_list()
    filename = file_list.pop(random.randrange(len(file_list)))
    if os.path.getsize('../images/' + filename) > LIMIT_SIZE:
        filename = file_list.pop(random.randrange(len(file_list)))
    while filename in seen_images:
        filename = file_list.pop(random.randrange(len(file_list)))
    if not restart:
        await ctx.send('', file=discord.File('../images/' + filename))
        write_viewed_image_list_for_guild(filename, guild_id)