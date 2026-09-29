"""Channel queries: which channels are active, and their posting schedule."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Channel
from app.db.repositories import guilds


@dataclass(frozen=True, slots=True)
class Schedule:
    """A channel's posting state, fetched in one query (§2.5).

    The old code needed three separate connections per poll to assemble this.
    """

    channel_id: int
    guild_id: int
    post_amount: int
    post_frequency: int
    last_post: datetime
    active: bool


async def get_schedule(session: AsyncSession, channel_id: int) -> Schedule | None:
    """Return the channel's full posting state, or ``None`` if it is unknown."""
    row = (
        await session.execute(
            select(
                Channel.id,
                Channel.guild_id,
                Channel.post_amount,
                Channel.post_frequency,
                Channel.last_post,
                Channel.active,
            ).where(Channel.id == channel_id)
        )
    ).one_or_none()
    return Schedule(*row) if row is not None else None


async def is_active(session: AsyncSession, channel_id: int) -> bool:
    """Whether the bot should be posting to this channel.

    An unknown channel is inactive, which is the inverse of the old
    ``is_channel_deleted`` returning ``True`` for a missing row.
    """
    return bool(await session.scalar(select(Channel.active).where(Channel.id == channel_id)))


async def active_ids(session: AsyncSession) -> list[int]:
    """Every channel id the bot should resume posting to on startup."""
    result = await session.scalars(select(Channel.id).where(Channel.active.is_(True)))
    return list(result)


async def active_schedules(session: AsyncSession) -> list[Schedule]:
    """Every active channel with its schedule, for resuming loops on startup.

    Returning ``guild_id`` from the database means the scheduler never has to
    re-derive it from the Discord channel object, which the old code did two
    different ways (§4.7).
    """
    rows = await session.execute(
        select(
            Channel.id,
            Channel.guild_id,
            Channel.post_amount,
            Channel.post_frequency,
            Channel.last_post,
            Channel.active,
        ).where(Channel.active.is_(True))
    )
    return [Schedule(*row) for row in rows]


async def ids_for_guild(session: AsyncSession, guild_id: int) -> list[int]:
    """Active channel ids within one guild."""
    result = await session.scalars(
        select(Channel.id).where(Channel.guild_id == guild_id, Channel.active.is_(True))
    )
    return list(result)


async def start(
    session: AsyncSession,
    channel_id: int,
    guild_id: int,
    *,
    post_amount: int,
    post_frequency: int,
    now: datetime | None = None,
) -> bool:
    """Register or re-activate a channel, setting its schedule.

    Replaces ``start_posting_entry`` plus the three follow-up setter calls, and names
    its columns rather than relying on table order (§2.8). Errors propagate rather
    than being logged and swallowed (§2.9).

    :return: ``True`` if this created a new channel, ``False`` if it reactivated one.
    """
    await guilds.ensure(session, guild_id)
    existing = await session.get(Channel, channel_id)

    if existing is None:
        session.add(
            Channel(
                id=channel_id,
                guild_id=guild_id,
                post_amount=post_amount,
                post_frequency=post_frequency,
                last_post=now or datetime.now(),
                active=True,
            )
        )
        return True

    existing.guild_id = guild_id
    existing.post_amount = post_amount
    existing.post_frequency = post_frequency
    existing.active = True
    return False


async def deactivate(session: AsyncSession, channel_id: int) -> None:
    """Stop posting to a channel."""
    await session.execute(update(Channel).where(Channel.id == channel_id).values(active=False))


async def set_post_amount(session: AsyncSession, channel_id: int, amount: int) -> None:
    """Set how many images go out per post."""
    await session.execute(update(Channel).where(Channel.id == channel_id).values(post_amount=amount))


async def set_post_frequency(session: AsyncSession, channel_id: int, frequency: int) -> None:
    """Set how many posts go out per window."""
    await session.execute(
        update(Channel).where(Channel.id == channel_id).values(post_frequency=frequency)
    )


async def set_last_post(session: AsyncSession, channel_id: int, when: datetime) -> None:
    """Record when the channel last received a post."""
    await session.execute(update(Channel).where(Channel.id == channel_id).values(last_post=when))


async def rewind_last_post(session: AsyncSession, channel_id: int, offset: timedelta) -> bool:
    """Move ``last_post`` back by ``offset`` so the next post lands sooner.

    Backs ``/posts reset_last_viewed``. With ``last_post`` stored as a real DATETIME
    (§3.5) this is plain ``timedelta`` arithmetic instead of the old juggling of
    ``datetime.fromtimestamp(float(...))``.

    :return: ``False`` if the channel is unknown.
    """
    schedule = await get_schedule(session, channel_id)
    if schedule is None:
        return False
    await set_last_post(session, channel_id, schedule.last_post - offset)
    return True
