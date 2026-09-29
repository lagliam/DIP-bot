"""Image catalog and per-guild send history."""

from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Guild, Image, SentImage
from app.db.repositories import guilds
from app.db.upsert import insert_ignore_statement


async def get_or_create(session: AsyncSession, filename: str, sha256: str, byte_size: int) -> int:
    """Return the catalog id for ``filename``, inserting it if it is new (§3.10).

    :param sha256: Content hash. Only read when the row is created, so callers can
        avoid hashing a file that is already catalogued.
    :return: ``images.id``.
    """
    image_id = await session.scalar(select(Image.id).where(Image.filename == filename))
    if image_id is not None:
        return image_id

    await session.execute(
        insert_ignore_statement(
            session,
            Image,
            {"filename": filename, "sha256": sha256, "byte_size": byte_size},
            index_elements=["filename"],
        )
    )
    # Re-read rather than trusting lastrowid: a concurrent insert may have won.
    image_id = await session.scalar(select(Image.id).where(Image.filename == filename))
    if image_id is None:  # pragma: no cover - only reachable if the insert vanished
        raise RuntimeError(f"Failed to catalog image {filename!r}")
    return image_id


async def id_for_filename(session: AsyncSession, filename: str) -> int | None:
    """Look up a catalog id without creating one."""
    return await session.scalar(select(Image.id).where(Image.filename == filename))


async def find_duplicates(session: AsyncSession) -> list[tuple[str, int]]:
    """Content hashes that appear under more than one filename.

    Made possible by the catalog's ``sha256`` index (§3.10).

    :return: ``(sha256, count)`` pairs.
    """
    rows = await session.execute(
        select(Image.sha256, func.count(Image.id))
        .group_by(Image.sha256)
        .having(func.count(Image.id) > 1)
    )
    return [(digest, count) for digest, count in rows]


async def seen_filenames(session: AsyncSession, guild_id: int) -> set[str]:
    """Filenames already sent to this guild in the current generation.

    One query, replacing the old one-``COUNT(*)``-per-candidate loop (§2.4).
    """
    generation = select(Guild.reset_generation).where(Guild.id == guild_id).scalar_subquery()
    result = await session.scalars(
        select(Image.filename)
        .join(SentImage, SentImage.image_id == Image.id)
        .where(SentImage.guild_id == guild_id, SentImage.generation == generation)
    )
    return set(result)


async def mark_sent(session: AsyncSession, guild_id: int, image_id: int) -> None:
    """Record that an image went out to a guild."""
    await guilds.ensure(session, guild_id)
    generation = await guilds.current_generation(session, guild_id)
    await session.execute(
        insert_ignore_statement(
            session,
            SentImage,
            {"guild_id": guild_id, "image_id": image_id, "generation": generation},
            index_elements=["guild_id", "image_id", "generation"],
        )
    )


async def reset_seen(session: AsyncSession, guild_id: int) -> int:
    """Put every image back into rotation for a guild.

    :return: The new generation.
    """
    return await guilds.bump_generation(session, guild_id)


async def total_sent(session: AsyncSession, guild_id: int) -> int:
    """How many images have ever been sent to a guild, across all generations."""
    total = await session.scalar(
        select(func.count(SentImage.id)).where(SentImage.guild_id == guild_id)
    )
    return total or 0


async def prune_old_generations(session: AsyncSession, guild_id: int) -> int:
    """Delete send history from before the current generation.

    Nothing calls this on the hot path; it exists so the table can be trimmed on a
    schedule rather than growing by the library size on every reset (§3.3).

    :return: Number of rows removed.
    """
    generation = await guilds.current_generation(session, guild_id)
    result = await session.execute(
        delete(SentImage).where(SentImage.guild_id == guild_id, SentImage.generation < generation)
    )
    return getattr(result, "rowcount", 0) or 0
