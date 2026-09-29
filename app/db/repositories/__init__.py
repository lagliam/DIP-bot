"""Query functions, grouped by the table they mostly touch.

Every function takes an :class:`~sqlalchemy.ext.asyncio.AsyncSession` as its first
argument rather than opening its own connection. That is what makes them testable
against an in-memory database, and it lets a caller batch several of them into one
transaction via :func:`app.db.session.session_scope`.
"""

from app.db.repositories import channels, guilds, images, reactions, reports, users

__all__ = ["channels", "guilds", "images", "reactions", "reports", "users"]
