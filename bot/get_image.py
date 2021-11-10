# get_image.py
# will return one image and mark as viewed
# returns true if image was sent, falst otherwise

from datetime import datetime
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
    while filename+'\n' in seen_images:
        try:
            filename = file_list.pop(random.randrange(len(file_list)))
        except(ValueError):
            filename = ''    
    if not restart and filename:
        await ctx.send('', file=discord.File('../images/' + filename))
        write_viewed_image_list_for_guild(filename, guild_id)
        return True
    if not filename:
        print(f'{datetime.now()}> out of images for {guild_id} ')
    
    return False
    