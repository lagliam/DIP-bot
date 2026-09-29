"""Logging setup, applied once at startup.

Replaces ``utility.log_event``, which called ``logging.basicConfig`` on every message
and wrote to an unbounded file.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_MAX_BYTES = 10_000_000
_BACKUP_COUNT = 5


def configure(path: Path = Path("log/dip-bot.log"), level: int = logging.INFO) -> None:
    """Attach a rotating file handler and a stream handler to the root logger.

    :param path: Log file to write to; its parent directory is created if missing.
    :param level: Minimum level to emit.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        handlers=[
            RotatingFileHandler(path, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT),
            logging.StreamHandler(),
        ],
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        level=level,
        force=True,
    )
    # These are chatty at INFO and drown out the bot's own messages.
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
