"""Dialect-aware upsert helpers.

The old code implemented upserts as ``SELECT id`` followed by a branch to ``INSERT`` or
``UPDATE`` (§2.7). Two reactions arriving at once both saw no row and both inserted.
These helpers push the whole thing into a single atomic statement backed by the unique
constraints declared in :mod:`app.db.models`.

MySQL and SQLite spell it differently, so the statement is built per dialect. SQLite
support exists because the test suite runs against aiosqlite rather than a container.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession


def _dialect(session: AsyncSession) -> str:
    return session.get_bind().dialect.name


def upsert_statement(
    session: AsyncSession,
    model: type[Any],
    values: Mapping[str, Any],
    *,
    index_elements: Sequence[str],
    update: Mapping[str, Any],
) -> Any:
    """Build an "insert, or update the conflicting row" statement.

    :param model: The mapped class to insert into.
    :param values: Column values for the INSERT.
    :param index_elements: Columns forming the unique constraint that may conflict.
    :param update: Column values to apply when the row already exists. Expressions
        such as ``Model.counter + 1`` refer to the *existing* row on both dialects.
    """
    name = _dialect(session)
    if name == "mysql":
        return mysql_insert(model).values(**values).on_duplicate_key_update(**update)
    if name == "sqlite":
        return sqlite_insert(model).values(**values).on_conflict_do_update(
            index_elements=list(index_elements), set_=dict(update)
        )
    raise NotImplementedError(f"Upsert is not implemented for dialect {name!r}")


def insert_ignore_statement(
    session: AsyncSession,
    model: type[Any],
    values: Mapping[str, Any],
    *,
    index_elements: Sequence[str],
) -> Any:
    """Build an "insert unless it already exists" statement.

    :param index_elements: Columns forming the unique constraint that may conflict.
    """
    name = _dialect(session)
    if name == "mysql":
        # MySQL has no INSERT ... ON CONFLICT DO NOTHING; assigning a column to itself
        # is the conventional no-op that still swallows the duplicate-key error.
        first = index_elements[0]
        return mysql_insert(model).values(**values).on_duplicate_key_update(
            **{first: getattr(model, first)}
        )
    if name == "sqlite":
        return sqlite_insert(model).values(**values).on_conflict_do_nothing(
            index_elements=list(index_elements)
        )
    raise NotImplementedError(f"Insert-ignore is not implemented for dialect {name!r}")
