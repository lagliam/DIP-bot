# send_image.py
# will return one image and mark as viewed
# returns true if image was sent, false otherwise

from datetime import datetime
import os
import random
import discord

import bot.database
from bot.constants import LIMIT_SIZE
from bot.utility import image_list, write_viewed_image_list_for_guild, get_all_seen_status, set_all_seen_status


async def send_image(ctx, guild_id, channel_id=None, restart=False):
    file_list = image_list()
    filename = file_list.pop(random.randrange(len(file_list)))
    while os.path.getsize('../images/' + filename) > LIMIT_SIZE:
        filename = file_list.pop(random.randrange(len(file_list)))
        print(f'{datetime.now()}> image {filename} too large to send')

    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE image is '{filename}'")
    is_image_seen = cur.fetchone()[0]

    while is_image_seen > 0:
        try:
            filename = file_list.pop(random.randrange(len(file_list)))
        except ValueError:
            filename = ''
        cur.execute(f"SELECT COUNT(*) FROM images WHERE image is '{filename}'")
        is_image_seen = cur.fetchone()[0]

    conn.close()

    if channel_id:
        is_all_seen = get_all_seen_status(channel_id)
    else:
        is_all_seen = False

    if not restart and filename:
        if channel_id:
            set_all_seen_status(channel_id, 'false')
        await ctx.send('', file=discord.File('../images/' + filename))
        write_viewed_image_list_for_guild(filename, guild_id)
        return True
    
    if not filename and not is_all_seen:
        print(f'{datetime.now()}> now out of images for {guild_id} ')
        set_all_seen_status(channel_id, 'true')

    if is_all_seen and restart:
        print(f'{datetime.now()}> reporting out of images for {guild_id} ')

    return False
