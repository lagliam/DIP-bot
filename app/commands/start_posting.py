import asyncio

from discord import ApplicationContext

from app.bot.main_loop import MainLoop
from app.utilities import text, database, utility


class StartPosting:
    """
    Class that represents StartPosting
    """

    def __init__(self, ctx: ApplicationContext, amount: int, frequency: int):
        """
        Parameters
        ----------
        :param ctx: The context object
        :type ctx: ApplicationContext
        :param amount: Amount to post at one time
        :type amount: int
        :param frequency:The number of times per day to post
        :type frequency: int
        """

        self._ctx = ctx
        self.amount = amount
        self.frequency = frequency
        self._channel_id = ctx.channel.id
        if ctx.channel.type.name == 'private':
            self._guild_id = ctx.user.id
        else:
            self._guild_id = ctx.channel.guild.id

    async def run(self) -> None:
        """
        Executes the logic to start posting
        """

        if not database.is_channel_deleted(self._channel_id):
            await self._ctx.respond(text.START_POSTING_REPEAT)
            return
        new_channel = False
        channel = database.get_channel(self._channel_id)
        if not channel:
            new_channel = True
            database.start_posting_entry(self._channel_id, self._guild_id)
        database.set_post_amount(self._channel_id, self.amount)
        database.set_post_frequency(self._channel_id, self.frequency)
        database.set_deleted_status(self._channel_id, False)
        await self._ctx.respond(text.START_POSTING)
        loop = self._start_posting(new_channel)
        await asyncio.create_task(loop.run())

    def _start_posting(self, is_new_channel: bool) -> MainLoop:
        """
        Gets a MainLoop object to start posting to a channel

        :param is_new_channel: Determines whether to format the log message to say restarting or starting
        :type is_new_channel: bool
        :return: The MainLoop object
        :rtype: MainLoop
        """

        if is_new_channel:
            utility.log_event(f'Started posting for guild {self._guild_id} channel {self._channel_id}')
        else:
            utility.log_event(f'Restarted posting for guild {self._guild_id} channel {self._channel_id}')
        return MainLoop({
            'ctx': self._ctx.channel,
            'guild_id': self._guild_id,
            'restart': not is_new_channel
        })
