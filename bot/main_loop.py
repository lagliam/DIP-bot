# main_loop.py
# main logic for sending images on an interval

import asyncio
import datetime
import os
import time

from bot.constants import RUNNING_FILE_POLL_INTERVAL, TRIGGER_DURATION
from bot.send_image import send_image
from bot.utility import get_posting_amount, get_posting_frequency, get_last_post_date, set_last_post_date


async def main_loop(ctx, running_file, guild_id, channel_id, restart=False):
    while os.path.exists(running_file):
        for _ in range(int(get_posting_amount(channel_id))):
            await send_image(ctx, guild_id, channel_id, restart)
        if not restart:
            set_last_post_date(channel_id, time.time())

        timestamp = datetime.datetime.fromtimestamp(float(get_last_post_date(channel_id)))

        start_waiting = (datetime.datetime.now() - timestamp).total_seconds()
        restart = False
        while start_waiting < (TRIGGER_DURATION / int(get_posting_frequency(channel_id))) \
                and os.path.exists(running_file):
            await asyncio.sleep(RUNNING_FILE_POLL_INTERVAL)
            start_waiting += RUNNING_FILE_POLL_INTERVAL
