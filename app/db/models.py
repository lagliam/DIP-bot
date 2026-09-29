"""SQLAlchemy models for the DIP-bot schema.

Design notes (see IMPROVEMENTS.md for the reasoning):

* ``images`` is a *catalog* keyed by an integer id, not by filename (§3.10). Everything
  that refers to an image points at ``images.id``, so renaming a file on disk keeps its
  likes, reports and seen-history intact.
* ``channels`` replaces the old ``guilds`` table, whose primary key was a channel id
  (§3.1). A real ``guilds`` table now exists and owns the per-guild reset counter.
* "Reset viewed" bumps ``guilds.reset_generation`` instead of soft-deleting every row
  (§3.3), so a reset is one UPDATE and old rows can be pruned.
* ``last_post`` is a real ``DATETIME`` (§3.5), which removes the float/timestamp
  round-tripping the old code did everywhere.

``BIG_INT`` carries a SQLite variant because Discord snowflakes need 64 bits on MySQL,
while SQLite needs plain ``INTEGER`` for a primary key to autoincrement. The test suite
runs the identical schema on aiosqlite.
"""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

#: 64-bit on MySQL, rowid-compatible on SQLite.
BIG_INT = BigInteger().with_variant(Integer, "sqlite")

#: ``users.guild_id`` sentinel meaning "not scoped to a guild", i.e. DM permission.
#: A sentinel rather than NULL because MySQL treats NULLs as distinct in unique
#: indexes, which would let duplicate DM rows through (§3.4).
NO_GUILD = 0

#: Constraint naming convention, so Alembic autogenerate produces stable names.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s",
    "pk": "pk_%(table_name)s",
}


class Permission(enum.IntEnum):
    """Authorization levels, mirroring rows in the ``bot_permissions`` table (§3.7)."""

    NONE = 1
    GUILD = 2
    PRIVATE = 3


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """``created``/``updated`` maintained by the database, not by Python (§3.6)."""

    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class BotPermission(Base):
    """Lookup table backing :class:`Permission`, kept for referential integrity."""

    __tablename__ = "bot_permissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)


class Guild(Base, TimestampMixin):
    """A posting scope: a Discord guild, or a user when the conversation is a DM."""

    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(BIG_INT, primary_key=True, autoincrement=False)
    #: Bumped by "reset viewed"; ``sent_images`` rows below this are history (§3.3).
    reset_generation: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class Channel(Base, TimestampMixin):
    """A channel the bot posts to, and its schedule."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(BIG_INT, primary_key=True, autoincrement=False)
    guild_id: Mapped[int] = mapped_column(
        BIG_INT, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_amount: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    post_frequency: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default="1")
    last_post: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    #: Replaces the old ``deleted`` flag; reads the right way round at the call sites.
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())


class Image(Base):
    """One row per image file the bot knows about (§3.10)."""

    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    #: Content hash, indexed but not unique so duplicate files are discoverable
    #: rather than rejected.
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    byte_size: Mapped[int] = mapped_column(BIG_INT, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class SentImage(Base):
    """An image that has been posted to a guild, used to avoid repeats (§3.2)."""

    __tablename__ = "sent_images"
    __table_args__ = (
        UniqueConstraint("guild_id", "image_id", "generation", name="uq_sent_images_guild_image_gen"),
        Index("ix_sent_images_guild_generation", "guild_id", "generation"),
    )

    id: Mapped[int] = mapped_column(BIG_INT, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(
        BIG_INT, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    #: Matches ``guilds.reset_generation`` at the time of sending.
    generation: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())


class _ImageCounter(TimestampMixin):
    """Shared shape for the per-(image, guild, channel) counters.

    ``channel_id`` deliberately has no foreign key: a DM channel can receive an image
    via ``/images get_one_image`` without ever being registered in ``channels``.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    counter: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")


class LikedImage(Base, _ImageCounter):
    """Reaction tally for an image in one channel."""

    __tablename__ = "liked_images"
    __table_args__ = (
        UniqueConstraint("image_id", "guild_id", "channel_id", name="uq_liked_images_image_guild_channel"),
    )

    image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    guild_id: Mapped[int] = mapped_column(
        BIG_INT, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[int] = mapped_column(BIG_INT, nullable=False)


class ReportedImage(Base, _ImageCounter):
    """Report tally for an image in one channel."""

    __tablename__ = "reported_images"
    __table_args__ = (
        UniqueConstraint(
            "image_id", "guild_id", "channel_id", name="uq_reported_images_image_guild_channel"
        ),
    )

    image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False
    )
    guild_id: Mapped[int] = mapped_column(
        BIG_INT, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False
    )
    channel_id: Mapped[int] = mapped_column(BIG_INT, nullable=False)


class User(Base, TimestampMixin):
    """Per-guild command authorization.

    The old ``deleted`` column is gone: revoking access sets ``permission`` back to
    :attr:`Permission.NONE`, so there is a single mechanism rather than two (§3.7).
    """

    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("user_id", "guild_id", name="uq_users_user_id_guild_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BIG_INT, nullable=False, index=True)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    #: ``NO_GUILD`` (0) for the DM scope.
    guild_id: Mapped[int] = mapped_column(BIG_INT, nullable=False, server_default=str(NO_GUILD))
    permission: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bot_permissions.id"),
        nullable=False,
        server_default=str(Permission.NONE.value),
    )
