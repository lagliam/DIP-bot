"""Discord-side helpers shared by the cogs."""

from __future__ import annotations

import logging
from pathlib import Path

import discord
from discord import ApplicationContext
from discord.abc import Messageable

from app.db import session_scope, users
from app.utilities import text

log = logging.getLogger(__name__)

_COGS_DIR = Path(__file__).resolve().parent.parent / "cogs"


def cog_names() -> list[str]:
    """Module names to load from ``app/cogs``.

    Derived from ``__file__`` rather than the process working directory, so the bot
    starts correctly regardless of where it is launched from (§4.6).
    """
    return sorted(path.stem for path in _COGS_DIR.glob("*.py") if not path.stem.startswith("_"))


def is_private(channel: Messageable | discord.abc.GuildChannel) -> bool:
    """Whether a channel is a direct message rather than part of a guild."""
    return isinstance(channel, discord.DMChannel) or getattr(channel, "guild", None) is None


def scope_id(ctx: ApplicationContext) -> int:
    """The id that owns posting state for this context.

    A guild id normally, or the invoking user's id in a DM. The old code inlined this
    branch in six places and spelled it two different ways (§4.7).
    """
    if ctx.guild is not None:
        return ctx.guild.id
    return ctx.user.id


async def check_permissions(ctx: ApplicationContext, bot: discord.Bot) -> bool:
    """Whether the caller may run this command, responding with a reason if not.

    Order matters: the bot owner always passes, then DMs need the ``private`` level,
    and guild commands need either guild ownership or an explicit grant.
    """
    if is_private(ctx.channel):
        await ctx.respond(text.PRIVATE_PERMISSIONS)
        return False

    if ctx.author.guild_permissions.administrator:
        return True

    if await bot.is_owner(ctx.author):
        return True

    if ctx.guild is not None and ctx.author.id == ctx.guild.owner_id:
        return True

    await ctx.respond(text.PERMISSIONS)
    return False
