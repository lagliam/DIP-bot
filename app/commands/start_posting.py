import asyncio

from app.bot.main_loop import MainLoop
from app.utilities import text, database, utility


class StartPosting:
    def __init__(self, ctx):
        self._ctx = ctx
        self._channel_id = ctx.channel.id
        if ctx.channel.type.name == 'private':
            self._guild_id = ctx.user.id
        else:
            self._guild_id = ctx.channel.guild.id

    async def run(self):
        channel = database.get_channel(self._channel_id)
        if channel:
            self._stop_posting()
            await self._ctx.respond(text.STOP_POSTING)
            return

        await self._ctx.respond(text.START_POSTING)
        loop = self._start_posting()
        await asyncio.create_task(loop.run())

    def _stop_posting(self):
        utility.log_event(f'Stop posting called for guild {self._guild_id} channel {self._channel_id}')
        database.delete_channel(self._channel_id)

    def _start_posting(self):
        database.start_posting_entry(self._channel_id, self._guild_id)
        utility.log_event(f'Started posting for guild {self._guild_id} channel {self._channel_id}')
        return MainLoop({
            'ctx': self._ctx.channel,
            'guild_id': self._guild_id,
            'restart': False
        })
