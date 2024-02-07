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
        if not database.is_channel_deleted(self._channel_id):
            await self._ctx.respond(text.START_POSTING_REPEAT)
            return
        new_channel = False
        channel = database.get_channel(self._channel_id)
        if not channel:
            new_channel = True
            database.start_posting_entry(self._channel_id, self._guild_id)
        database.set_deleted_status(self._channel_id, False)
        await self._ctx.respond(text.START_POSTING)
        loop = self._start_posting(new_channel)
        await asyncio.create_task(loop.run())

    def _start_posting(self, is_new_channel: bool):
        utility.log_event(f'Started posting for guild {self._guild_id} channel {self._channel_id}')
        return MainLoop({
            'ctx': self._ctx.channel,
            'guild_id': self._guild_id,
            'restart': not is_new_channel
        })
