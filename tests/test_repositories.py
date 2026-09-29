"""Regression tests for the database fixes in IMPROVEMENTS.md."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import NO_GUILD, Base, Permission
from app.db.repositories import images, reactions, reports, users


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """An isolated SQLite schema; production uses the same models with MySQL."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as database_session:
        yield database_session
        await database_session.rollback()
    await engine.dispose()


@pytest.mark.asyncio
async def test_private_permission_uses_the_dm_scope(session: AsyncSession) -> None:
    """DM permission is queryable; the legacy ``= NULL`` query never was."""
    await users.grant(session, 42, "tester", NO_GUILD, Permission.PRIVATE)
    await session.commit()

    assert await users.has_private_permission(session, 42)


@pytest.mark.asyncio
async def test_empty_and_populated_reaction_counters(session: AsyncSession) -> None:
    """Top-liked and report-count queries safely handle their first row."""
    assert await reactions.top_liked_filename(session, 10, 20) is None

    image_id = await images.get_or_create(session, "picture.jpg", "a" * 64, 123)
    await reactions.add_like(session, image_id, 10, 20)
    assert await reports.report_count(session, image_id, 10, 20) == 0
    assert await reports.log_report(session, image_id, 10, 20) == 1
    await session.commit()

    assert await reactions.top_liked_filename(session, 10, 20) == "picture.jpg"
    assert await reports.report_count(session, image_id, 10, 20) == 1
