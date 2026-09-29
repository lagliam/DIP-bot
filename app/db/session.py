"""Async engine and session management.

Replaces ``database.database_connection``, which opened a fresh TCP connection for
every query and closed it outside any ``try``/``finally`` (§2.2). The engine here owns
a connection pool for the process lifetime, and :func:`session_scope` guarantees the
session is committed on success and rolled back on failure.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

log = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def init_engine(url: str, *, echo: bool = False) -> AsyncEngine:
    """Create the process-wide engine and session factory.

    Safe to call more than once; later calls with the same URL are a no-op.

    :param url: SQLAlchemy async URL, e.g. ``mysql+asyncmy://user:pass@host/db``.
    :param echo: Log every statement. Noisy; for debugging only.
    :return: The engine.
    """
    global _engine, _sessionmaker

    if _engine is not None:
        if str(_engine.url) == url:
            return _engine
        raise RuntimeError("init_engine called twice with different URLs")

    # SQLite (the test backend) does not accept pool sizing arguments.
    pool_kwargs: dict[str, object] = {}
    if not url.startswith("sqlite"):
        pool_kwargs = {
            "pool_size": 10,
            "max_overflow": 5,
            "pool_recycle": 3600,  # MySQL drops idle connections after 8h by default
            "pool_pre_ping": True,  # survive a database restart without a crash loop
        }

    _engine = create_async_engine(url, echo=echo, **pool_kwargs)
    # expire_on_commit=False keeps loaded objects usable after the session closes,
    # which matters because repository functions return ORM objects to the callers.
    _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_engine() -> AsyncEngine:
    """Return the engine, raising if :func:`init_engine` has not run."""
    if _engine is None:
        raise RuntimeError("Database engine not initialised; call init_engine() first")
    return _engine


async def dispose_engine() -> None:
    """Close every pooled connection. Call on shutdown."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None


@asynccontextmanager
async def session_scope() -> AsyncIterator[AsyncSession]:
    """Yield a session inside a transaction, committing or rolling back on exit.

    ::

        async with session_scope() as session:
            await channels.set_post_amount(session, channel_id, 3)
    """
    if _sessionmaker is None:
        raise RuntimeError("Database engine not initialised; call init_engine() first")

    session = _sessionmaker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
