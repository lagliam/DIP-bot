"""Command authorization."""

from __future__ import annotations

from discord import ApplicationContext
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import NO_GUILD, Permission, User
from app.db.upsert import upsert_statement

_CONFLICT = ("user_id", "guild_id")


async def grant(
    session: AsyncSession,
    user_id: int,
    user_name: str,
    guild_id: int,
    permission: Permission = Permission.GUILD,
) -> None:
    """Authorize a user to run commands in a guild."""
    await session.execute(
        upsert_statement(
            session,
            User,
            {
                "user_id": user_id,
                "user_name": user_name,
                "guild_id": guild_id,
                "permission": int(permission),
            },
            index_elements=_CONFLICT,
            update={
                "permission": int(permission),
                "user_name": user_name,
                "updated": func.now(),
            },
        )
    )


async def revoke(session: AsyncSession, user_id: int, guild_id: int) -> None:
    """Drop a user back to :attr:`Permission.NONE`."""
    await session.execute(
        upsert_statement(
            session,
            User,
            {
                "user_id": user_id,
                "user_name": "",
                "guild_id": guild_id,
                "permission": int(Permission.NONE),
            },
            index_elements=_CONFLICT,
            update={"permission": int(Permission.NONE), "updated": func.now()},
        )
    )


async def permission_for(session: AsyncSession, user_id: int, guild_id: int) -> Permission:
    """The user's permission level in a guild, defaulting to :attr:`Permission.NONE`."""
    level = await session.scalar(
        select(User.permission).where(User.user_id == user_id, User.guild_id == guild_id)
    )
    return Permission(level) if level else Permission.NONE


async def has_guild_permission(session: AsyncSession, user_id: int, guild_id: int) -> bool:
    """Whether the user may run commands in this guild."""
    return await permission_for(session, user_id, guild_id) >= Permission.GUILD


async def has_private_permission(session: AsyncSession, user_id: int) -> bool:
    """Whether the user may run commands in a DM.

    DM authorization is stored against the ``NO_GUILD`` sentinel. The old query used
    ``WHERE guild_id = NULL``, which is never true in SQL, so this permission level
    could never be granted to anyone (§1.1).
    """
    return await permission_for(session, user_id, NO_GUILD) >= Permission.PRIVATE
