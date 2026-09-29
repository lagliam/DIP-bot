"""Runtime configuration, read from the environment exactly once.

Replaces the old ``app.utilities.constants`` module and the per-query ``os.getenv``
calls in the old ``database.database_connection``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

#: Image extensions the bot is willing to post.
IMAGE_SUFFIXES = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp"})


@dataclass(frozen=True, slots=True)
class Config:
    """Everything the bot needs to start, resolved from the environment."""

    discord_token: str
    database_url: str

    images_path: Path = Path("images")
    reported_path: Path = Path("reported_images")
    log_path: Path = Path("log/dip-bot.log")
    #: Where compressed copies of oversized images are written. Kept outside
    #: ``images_path`` so generated files are never picked up as postable content,
    #: and separate from the originals so compression is non-destructive (§4.9).
    cache_path: Path = Path("var/compressed")

    #: Discord's attachment ceiling for an unboosted server.
    max_attachment_bytes: int = 8_000_000
    #: The window that ``post_frequency`` divides up; one post per window per frequency.
    trigger_duration: timedelta = field(default_factory=lambda: timedelta(days=1))
    #: How often a channel loop re-checks whether it is due to post.
    poll_interval: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    #: Reports needed before an image is copied to ``reported_path`` for review.
    report_threshold: int = 5

    def post_interval(self, frequency: int) -> timedelta:
        """Time between posts for a channel posting ``frequency`` times per window."""
        return self.trigger_duration / max(frequency, 1)


def database_url() -> str:
    """Build a SQLAlchemy async URL from the DB_* variables.

    ``DATABASE_URL`` overrides the lot, which is what the test suite and any
    non-MySQL deployment use.

    Public because Alembic needs it without needing a Discord token.
    """
    if override := os.getenv("DATABASE_URL"):
        return override

    user = os.getenv("DB_USER", "")
    password = os.getenv("DB_PASS", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "db")
    # Passwords routinely contain characters that are not URL-safe.
    return f"mysql+asyncmy://{quote_plus(user)}:{quote_plus(password)}@{host}:{port}/{name}"


@lru_cache(maxsize=1)
def get_config() -> Config:
    """Load and cache the configuration.

    Cached so that importing this module has no side effects and tests can clear it
    with ``get_config.cache_clear()``.
    """
    load_dotenv(Path(".env"))

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set; copy .env.example to .env and fill it in")

    return Config(
        discord_token=token,
        database_url=database_url(),
        images_path=Path(os.getenv("IMAGES_PATH", "images")),
        reported_path=Path(os.getenv("REPORTED_PATH", "reported_images")),
        log_path=Path(os.getenv("LOG_PATH", "log/dip-bot.log")),
        cache_path=Path(os.getenv("CACHE_PATH", "var/compressed")),
    )
