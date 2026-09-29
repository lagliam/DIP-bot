"""The ``/help`` command."""

from __future__ import annotations

import discord
from discord import ApplicationContext
from discord.ext import commands

from app.bot.client import DipBot
from app.utilities import text
from app.utilities.discord_utils import check_permissions


class Help(commands.Cog):
    """Describes the bot and its most-used commands."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    @discord.command(description=text.HELP_HELP)
    async def help(self, ctx: ApplicationContext) -> None:
        """Show bot info and a short command list."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        name = self.bot.user.name if self.bot.user else "DIP-bot"
        embed = discord.Embed(
            title=name,
            description=text.bot_description(name),
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Popular Commands", value=text.POPULAR_COMMANDS, inline=False)
        embed.add_field(name="Command Groups", value=text.COMMAND_GROUPS, inline=False)
        await ctx.respond(embed=embed)


def setup(bot: DipBot) -> None:
    bot.add_cog(Help(bot))
