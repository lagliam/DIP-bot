# main_loop.py
# main logic for sending images on an interval

import asyncio
import os
import datetime
import time

from bot.constants import RUNNING_FILE_POLL_INTERVAL
from bot.constants import TRIGGER_DURATION
from bot.get_image import send_image
from bot.utility import file_to_array, get_posting_amount, \
    get_posting_frequency, get_last_post_date, set_last_post_date


async def main_loop(ctx, running_file, guild_id, channel_id, restart=False):
    while os.path.exists(running_file):
        seen_images = file_to_array(f'../guilds/images_{guild_id}.txt')
        for _ in range(int(get_posting_amount(
                guild_id, channel_id))):
            await send_image(ctx, seen_images, guild_id, channel_id, restart)
        if not restart:
            set_last_post_date(guild_id, channel_id, time.time())

        timestamp = datetime.datetime.fromtimestamp(
            float(get_last_post_date(guild_id, channel_id)))

        start_waiting = (datetime.datetime.now() - timestamp).total_seconds()
        restart = False
        while start_waiting < (TRIGGER_DURATION / int(get_posting_frequency(
                guild_id, channel_id))) \
                and os.path.exists(running_file):
            await asyncio.sleep(RUNNING_FILE_POLL_INTERVAL)
            start_waiting += RUNNING_FILE_POLL_INTERVAL
