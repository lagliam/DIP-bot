"""Report tallies for posted images."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ReportedImage
from app.db.repositories import guilds
from app.db.upsert import upsert_statement

_CONFLICT = ("image_id", "guild_id", "channel_id")


async def log_report(session: AsyncSession, image_id: int, guild_id: int, channel_id: int) -> int:
    """Record a report and return the running total for that image in that channel.

    The old code did this as two public functions, ``log_report`` then
    ``get_report_count``, and the second raised ``TypeError`` when no row existed
    (§1.2). Folding them together removes both the extra round trip and the crash.
    """
    await guilds.ensure(session, guild_id)
    await session.execute(
        upsert_statement(
            session,
            ReportedImage,
            {"image_id": image_id, "guild_id": guild_id, "channel_id": channel_id, "counter": 1},
            index_elements=_CONFLICT,
            update={"counter": ReportedImage.counter + 1, "updated": func.now()},
        )
    )
    count = await session.scalar(
        select(ReportedImage.counter).where(
            ReportedImage.image_id == image_id,
            ReportedImage.guild_id == guild_id,
            ReportedImage.channel_id == channel_id,
        )
    )
    return count or 0


async def report_count(session: AsyncSession, image_id: int, guild_id: int, channel_id: int) -> int:
    """How many reports an image has in a channel; 0 when it has never been reported."""
    count = await session.scalar(
        select(ReportedImage.counter).where(
            ReportedImage.image_id == image_id,
            ReportedImage.guild_id == guild_id,
            ReportedImage.channel_id == channel_id,
        )
    )
    return count or 0
