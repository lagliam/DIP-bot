# startup.py
# prepares and manages the restart process

import asyncio
from datetime import datetime
import glob
import os

from bot.main_loop import main_loop


async def check_running(bot):
    print(f'{datetime.now()}> Im restarting!')
    os.chdir("guilds")
    for file in glob.glob("*.running"):
        file_parts = file.split('.')  # need the channel id
        if file_parts:
            channel = bot.get_channel(int(file_parts[1]))
            asyncio.create_task(main_loop(channel, file, file_parts[0], file_parts[1],
                                          restart=True))
