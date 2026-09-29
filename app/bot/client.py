"""The bot subclass that carries shared state.

Cogs reach the scheduler and configuration through ``self.bot`` rather than through
module-level globals, which keeps them constructible in tests.
"""

from __future__ import annotations

import discord

from app.bot.scheduler import PostingScheduler
from app.config import Config
from app.db import dispose_engine


class DipBot(discord.Bot):
    """``discord.Bot`` plus the scheduler and configuration."""

    def __init__(self, config: Config, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.scheduler = PostingScheduler(self, config)

    async def close(self) -> None:
        """Cancel posting loops and close the connection pool before shutting down.

        ``discord.Bot.run`` calls this on SIGINT/SIGTERM, so the systemd units get a
        clean stop rather than a killed process holding MySQL connections open.
        """
        await self.scheduler.shutdown()
        await dispose_engine()
        await super().close()
