"""Guild-scope queries: the posting scope and its reset generation."""

from __future__ import annotations

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Guild
from app.db.upsert import insert_ignore_statement


async def ensure(session: AsyncSession, guild_id: int) -> None:
    """Create the guild row if it does not exist.

    Every table that references ``guilds.id`` needs this first. Cheap and idempotent.
    """
    await session.execute(
        insert_ignore_statement(session, Guild, {"id": guild_id}, index_elements=["id"])
    )


async def current_generation(session: AsyncSession, guild_id: int) -> int:
    """Return the guild's reset generation, or 0 if the guild is unknown."""
    generation = await session.scalar(select(Guild.reset_generation).where(Guild.id == guild_id))
    return generation or 0


async def bump_generation(session: AsyncSession, guild_id: int) -> int:
    """Advance the reset generation, putting every sent image back into rotation.

    This is the §3.3 replacement for soft-deleting every ``images`` row on reset.

    :return: The new generation.
    """
    await ensure(session, guild_id)
    await session.execute(
        update(Guild)
        .where(Guild.id == guild_id)
        .values(reset_generation=Guild.reset_generation + 1)
    )
    return await current_generation(session, guild_id)
