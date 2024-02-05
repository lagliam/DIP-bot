# app.py
# The main entry point into the application

import asyncio

import discord

from app.bot.main_loop import MainLoop
from app.utilities import database, utility


class App:
    def __init__(self, bot: discord.Bot):
        self._bot = bot

    async def run(self):
        channels = database.get_channels()
        channels_list = []
        for t in channels:
            channels_list.append(await self._bot.fetch_channel(t[0]))
        tasks = self._startup_tasks(channels_list)
        utility.log_event(f'Found {len(tasks)} coroutines to start')
        await asyncio.gather(*tasks)
        utility.log_event('Coroutines ended')

    @staticmethod
    def _startup_tasks(channels):
        utility.log_event('Bot starting')
        tasks = []
        for channel in channels:
            if channel.type.name == 'private':
                guild_id = channel.recipient.id
            else:
                guild_id = channel.guild.id
            params = {
                'ctx': channel,
                'guild_id': guild_id,
                'restart': True
            }
            main_loop = MainLoop(params)
            tasks.append(main_loop.run())
        return tasks
