import asyncio

import discord

from app.bot.main_loop import MainLoop
from app.utilities import database, utility


class App:
    """
    Class used to represent the main loop for image send scheduling
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        """

        self._bot = bot

    async def run(self) -> None:
        """
        Gathers the channels to run from the database and executes the loops
        """

        channels = database.get_active_channels()
        channels_list = []
        for t in channels:
            channels_list.append(await self._bot.fetch_channel(t[0]))
        tasks = self._startup_tasks(channels_list)
        utility.log_event(f'Found {len(tasks)} coroutines to start')
        await asyncio.gather(*tasks)
        utility.log_event('Coroutines ended')

    @staticmethod
    def _startup_tasks(channels: list) -> list:
        """
        Takes a list of channels and creates MainLoop objects

        :param channels: The list of channels to start
        :type channels: list
        :return: The tasks of MainLoop.run() coroutines to execute
        :rtype: list
        """

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
