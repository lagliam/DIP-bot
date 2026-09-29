"""Alembic environment, wired to the app's models and async engine.

The database URL comes from the application configuration rather than
``alembic.ini`` (§3.9 follow-on): one source of truth, and no credentials checked into
a config file. ``target_metadata`` is set, so ``alembic revision --autogenerate`` works.
"""

from __future__ import annotations

import asyncio
import pathlib
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Make the application importable when alembic runs from the project root.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.config import database_url
from app.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# An explicit -x url=... beats the environment, which helps when migrating a
# non-default database.
_override = context.get_x_argument(as_dictionary=True).get("url")
config.set_main_option("sqlalchemy.url", _override or database_url())


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of running it."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations against an already-open synchronous connection."""
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Open an async engine and drive the migrations through it."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
