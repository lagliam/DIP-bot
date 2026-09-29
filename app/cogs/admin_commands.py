"""The ``/admin`` command group."""

from __future__ import annotations

import logging

import discord
from discord import ApplicationContext, NotFound
from discord.ext import commands

from app.bot.client import DipBot
from app.commands.report import Report
from app.db import session_scope, users
from app.utilities import text
from app.utilities.discord_utils import check_permissions, is_private, scope_id

log = logging.getLogger(__name__)


class AdminCommands(commands.Cog):
    """Health, authorization and reporting."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    admin = discord.SlashCommandGroup("admin", "Part of the admin features")

    @admin.command(description=text.HEALTH_CHECK_HELP)
    async def health_check(self, ctx: ApplicationContext) -> None:
        """Confirm the bot is alive and responding."""
        await ctx.defer(ephemeral=True)
        if await check_permissions(ctx, self.bot):
            await ctx.respond(text.HEALTH_CHECK_RESPONSE)

def setup(bot: DipBot) -> None:
    bot.add_cog(AdminCommands(bot))
