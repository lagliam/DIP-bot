"""Turning raw Discord reaction events into like-counter updates."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import discord

from app.db import images, reactions, session_scope

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReactionTarget:
    """What a reaction event resolved to.

    A typed record rather than the old ``dict`` of loose keys (§4.2).
    """

    filename: str
    guild_id: int
    channel_id: int


async def handle(bot: discord.Bot, payload: discord.RawReactionActionEvent, *, added: bool) -> None:
    """Apply a reaction add/remove to the image's like counter.

    Silently does nothing when the reaction is not on a bot-posted image, which is
    the common case on a busy server.

    :param added: ``True`` for a reaction add, ``False`` for a remove.
    """
    target = await resolve(bot, payload)
    if target is None:
        return

    async with session_scope() as session:
        image_id = await images.id_for_filename(session, target.filename)
        if image_id is None:
            # The bot posted it before the catalog existed, or the file was renamed.
            log.debug("Reaction on uncatalogued image %s, ignoring", target.filename)
            return
        if added:
            await reactions.add_like(session, image_id, target.guild_id, target.channel_id)
        else:
            await reactions.remove_like(session, image_id, target.guild_id, target.channel_id)


async def resolve(
    bot: discord.Bot, payload: discord.RawReactionActionEvent
) -> ReactionTarget | None:
    """Fetch the reacted-to message and extract the image it carries.

    :return: ``None`` unless the message was posted by this bot and has an attachment.
    """
    if bot.user is None or payload.user_id == bot.user.id:
        return None  # the bot's own reactions do not count

    messageable = bot.get_partial_messageable(payload.channel_id)
    try:
        message = await messageable.fetch_message(payload.message_id)
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None

    # Compare ids, not display names: two accounts can share a name.
    if message.author.id != bot.user.id or not message.attachments:
        return None

    # In a DM there is no guild, so the reacting user is the posting scope.
    guild_id = payload.guild_id if payload.guild_id is not None else payload.user_id
    return ReactionTarget(
        filename=message.attachments[0].filename,
        guild_id=guild_id,
        channel_id=payload.channel_id,
    )
