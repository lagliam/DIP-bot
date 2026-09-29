"""Reaction tallies for posted images."""

from __future__ import annotations

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Image, LikedImage
from app.db.repositories import guilds
from app.db.upsert import upsert_statement

_CONFLICT = ("image_id", "guild_id", "channel_id")


async def add_like(session: AsyncSession, image_id: int, guild_id: int, channel_id: int) -> None:
    """Increment an image's like counter for a channel.

    A single atomic statement rather than the old SELECT-then-branch, which lost
    increments when two reactions landed together (§2.7).
    """
    await guilds.ensure(session, guild_id)
    await session.execute(
        upsert_statement(
            session,
            LikedImage,
            {"image_id": image_id, "guild_id": guild_id, "channel_id": channel_id, "counter": 1},
            index_elements=_CONFLICT,
            update={"counter": LikedImage.counter + 1, "updated": func.now()},
        )
    )


async def remove_like(session: AsyncSession, image_id: int, guild_id: int, channel_id: int) -> None:
    """Decrement an image's like counter, never going below zero.

    Unlike the old version this cannot drive the counter negative when a reaction is
    removed that the bot never recorded (e.g. added while the bot was down).
    """
    await session.execute(
        update(LikedImage)
        .where(
            LikedImage.image_id == image_id,
            LikedImage.guild_id == guild_id,
            LikedImage.channel_id == channel_id,
        )
        .values(
            counter=case((LikedImage.counter > 0, LikedImage.counter - 1), else_=0),
            updated=func.now(),
        )
    )


async def top_liked_filename(session: AsyncSession, guild_id: int, channel_id: int) -> str | None:
    """The most-reacted-to image in a channel.

    Ordering happens in SQL (§2.6), and an empty result returns ``None`` instead of
    raising ``IndexError`` (§1.2).
    """
    return await session.scalar(
        select(Image.filename)
        .join(LikedImage, LikedImage.image_id == Image.id)
        .where(
            LikedImage.guild_id == guild_id,
            LikedImage.channel_id == channel_id,
            LikedImage.counter > 0,
        )
        .order_by(LikedImage.counter.desc(), Image.filename)
        .limit(1)
    )
