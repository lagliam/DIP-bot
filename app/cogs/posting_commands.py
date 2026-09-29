"""The ``/posts`` command group."""

from __future__ import annotations

import logging
from datetime import datetime

import discord
from discord import ApplicationContext
from discord.ext import commands

from app.bot.client import DipBot
from app.db import channels, images, session_scope
from app.utilities import text
from app.utilities.discord_utils import check_permissions, is_private, scope_id

log = logging.getLogger(__name__)


class PostingCommands(commands.Cog):
    """Commands that inspect and adjust a channel's posting schedule."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    posting_commands = discord.SlashCommandGroup("posts", "Part of the image posting features")

    @posting_commands.command(description=text.NEXT_POST_DETAILS_HELP)
    async def next_post_details(self, ctx: ApplicationContext) -> None:
        """Report how many images are queued and when they go out."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        # One query for the whole row, where the old code made three (§2.5).
        async with session_scope() as session:
            schedule = await channels.get_schedule(session, ctx.channel.id)

        if schedule is None or not schedule.active:
            await ctx.respond(text.POSTING_NOT_STARTED)
            return

        due_at = schedule.last_post + self.bot.config.post_interval(schedule.post_frequency)
        minutes = max(int((due_at - datetime.now()).total_seconds() // 60), 0)
        await ctx.respond(
            f"The next post of {schedule.post_amount} image(s) will be in {minutes} minutes"
        )

    @posting_commands.command(description=text.POST_AMOUNT_HELP)
    async def posting_amount(
        self,
        ctx: ApplicationContext,
        amount: discord.Option(int, choices=[1, 2, 3, 4, 5]),  # type: ignore[valid-type]
    ) -> None:
        """Set how many images go out per post."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        async with session_scope() as session:
            if not await channels.is_active(session, ctx.channel.id):
                await ctx.respond(text.POSTING_NOT_STARTED)
                return
            await channels.set_post_amount(session, ctx.channel.id, amount)
        await ctx.respond(text.POST_AMOUNT_END)

    @posting_commands.command(description=text.CHANGE_FREQUENCY_HELP)
    async def change_frequency(
        self,
        ctx: ApplicationContext,
        amount: discord.Option(int, choices=[1, 2, 3, 4, 5]),  # type: ignore[valid-type]
    ) -> None:
        """Set how many posts go out per day."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        async with session_scope() as session:
            if not await channels.is_active(session, ctx.channel.id):
                await ctx.respond(text.POSTING_NOT_STARTED)
                return
            await channels.set_post_frequency(session, ctx.channel.id, amount)
        await ctx.respond(text.CHANGE_FREQUENCY_END)

    @posting_commands.command(description=text.RESET_LAST_VIEWED_HELP)
    async def reset_last_viewed(self, ctx: ApplicationContext) -> None:
        """Pull the next post forward to within one poll interval."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        async with session_scope() as session:
            schedule = await channels.get_schedule(session, ctx.channel.id)
            if schedule is None or not schedule.active:
                await ctx.respond(text.POSTING_NOT_STARTED)
                return
            # Rewind just far enough that the loop finds the post due one poll from now.
            offset = (
                self.bot.config.post_interval(schedule.post_frequency)
                - self.bot.config.poll_interval
            )
            await channels.rewind_last_post(session, ctx.channel.id, offset)
        await ctx.respond(text.RESET_LAST_VIEWED_RESPONSE)

    @posting_commands.command(description=text.RESET_VIEWED_HELP)
    async def reset_viewed(self, ctx: ApplicationContext) -> None:
        """Put every previously-posted image back into rotation."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        # A single generation bump rather than a soft-delete of every row (§3.3).
        async with session_scope() as session:
            await images.reset_seen(session, scope_id(ctx))
        await ctx.respond(text.RESET_VIEWED_MESSAGE)

    @posting_commands.command(description=text.STATS_HELP)
    async def stats(self, ctx: ApplicationContext) -> None:
        """Show totals for this guild."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        guild_id = scope_id(ctx)
        async with session_scope() as session:
            post_total = await images.total_sent(session, guild_id)
            channel_ids = (
                [] if is_private(ctx.channel) else await channels.ids_for_guild(session, guild_id)
            )

        if is_private(ctx.channel):
            guild_name = "Private Messages"
            channel_names = "DM Channel"
        else:
            guild_name = ctx.guild.name
            names = [
                channel.name
                for channel in (self.bot.get_channel(cid) for cid in channel_ids)
                if channel is not None
            ]
            channel_names = ", ".join(names) if names else "None"

        embed = discord.Embed(
            title=f"Bot Stats for {guild_name}",
            description=text.STATS_HELP,
            color=discord.Colour.blurple(),
        )
        embed.add_field(name="Total images sent", value=f"Sent: {post_total}")
        embed.add_field(name="Channels being posted to", value=channel_names)
        await ctx.respond(embed=embed)


def setup(bot: DipBot) -> None:
    bot.add_cog(PostingCommands(bot))
