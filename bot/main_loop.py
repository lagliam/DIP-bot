# main_loop.py
# main logic for sending images on an interval

import asyncio
import os

from bot.constants import RUNNING_FILE_POLL_INTERVAL
from bot.constants import TRIGGER_DURATION
from bot.get_image import send_image
from bot.utility import image_list, file_to_array, get_posting_amount, \
    get_posting_frequency


async def main_loop(ctx, running_file, guild_id, channel_id, restart=False):
    # await ctx.send('(o･｀Д´･o) Baka!')
    counter = 0
    seen_images = file_to_array(f'../guilds/images_{guild_id}.txt')
    if not restart:
        for _ in range(int(get_posting_amount(
                guild_id, channel_id))):
            await send_image(ctx, seen_images, guild_id, restart)

    while counter < (len(image_list()) - len(seen_images)) and os.path.exists(
            running_file):
        counter += 1
        for _ in range(int(get_posting_amount(
                guild_id, channel_id))):
            await send_image(ctx, seen_images, guild_id, restart)
        start_waiting = 0
        restart = False
        while start_waiting < (TRIGGER_DURATION / int(get_posting_frequency(
                guild_id, channel_id))) \
                and os.path.exists(running_file):
            await asyncio.sleep(RUNNING_FILE_POLL_INTERVAL)
            start_waiting += RUNNING_FILE_POLL_INTERVAL
