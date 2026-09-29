"""The ``/stop`` command."""

from __future__ import annotations

import logging

import discord
from discord import ApplicationContext
from discord.ext import commands

from app.bot.client import DipBot
from app.db import channels, session_scope
from app.utilities import text
from app.utilities.discord_utils import check_permissions

log = logging.getLogger(__name__)


class Stop(commands.Cog):
    """Ends scheduled posting in a channel."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    @discord.command(description=text.STOP_POSTING_HELP)
    async def stop(self, ctx: ApplicationContext) -> None:
        """Stop posting in the channel this was called from."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        async with session_scope() as session:
            if not await channels.is_active(session, ctx.channel.id):
                await ctx.respond(text.STOP_POSTING_REPEAT)
                return
            await channels.deactivate(session, ctx.channel.id)

        # Cancel the task too, so the stop is immediate rather than taking effect on
        # the loop's next tick.
        self.bot.scheduler.stop(ctx.channel.id)
        log.info("Stopped posting for channel %s", ctx.channel.id)
        await ctx.respond(text.STOP_POSTING)


def setup(bot: DipBot) -> None:
    bot.add_cog(Stop(bot))
