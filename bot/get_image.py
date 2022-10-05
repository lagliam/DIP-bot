# get_image.py
# will return one image and mark as viewed
# returns true if image was sent, false otherwise

from datetime import datetime
import os
import random
import discord

from bot.constants import LIMIT_SIZE
from bot.utility import image_list, write_viewed_image_list_for_guild, get_all_seen_status, set_all_seen_status


async def send_image(ctx, seen_images, guild_id, channel_id=None, restart=False):
    file_list = image_list()
    filename = file_list.pop(random.randrange(len(file_list)))
    while os.path.getsize('../images/' + filename) > LIMIT_SIZE:
        filename = file_list.pop(random.randrange(len(file_list)))
        print(f'{datetime.now()}> image {filename} too large to send')
    while filename+'\n' in seen_images:
        try:
            filename = file_list.pop(random.randrange(len(file_list)))
        except ValueError:
            filename = ''

    if channel_id:
        is_all_seen = get_all_seen_status(guild_id, channel_id)
    else:
        is_all_seen = False

    if not restart and filename:
        if channel_id:
            set_all_seen_status(guild_id, channel_id, 'false')
        await ctx.send('', file=discord.File('../images/' + filename))
        write_viewed_image_list_for_guild(filename, guild_id)
        return True
    
    if not filename and not is_all_seen:
        print(f'{datetime.now()}> now out of images for {guild_id} ')
        set_all_seen_status(guild_id, channel_id, 'true')

    if is_all_seen and restart:
        print(f'{datetime.now()}> reporting out of images for {guild_id} ')

    return False
