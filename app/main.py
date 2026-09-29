"""Process entry point.

The old ``bot.py`` did all of this at import time, which made the module impossible to
import from a test (§4.8). Everything now happens inside :func:`main`.
"""

from __future__ import annotations

import logging

import discord

from app import logging_config
from app.bot import reactions as reaction_events
from app.bot.client import DipBot
from app.config import Config, get_config
from app.db import init_engine
from app.utilities.discord_utils import cog_names

log = logging.getLogger(__name__)


def build_bot(config: Config) -> DipBot:
    """Construct the bot, load its cogs and register the gateway event handlers."""
    # Default intents cover guild and DM reactions, which is all the bot listens for.
    bot = DipBot(config, intents=discord.Intents.default())

    for name in cog_names():
        bot.load_extension(f"app.cogs.{name}")
        log.debug("Loaded cog %s", name)

    @bot.event
    async def on_ready() -> None:
        """Resume posting loops once the gateway connection is up."""
        log.info("Connected to Discord as %s", bot.user)
        # on_ready fires again after a reconnect; the scheduler ignores channels that
        # already have a live loop.
        await bot.scheduler.resume_all()

    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
        await reaction_events.handle(bot, payload, added=True)

    @bot.event
    async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent) -> None:
        await reaction_events.handle(bot, payload, added=False)

    return bot


def main() -> None:
    """Configure logging and the database, then run the bot until it is stopped."""
    config = get_config()
    logging_config.configure(config.log_path)
    init_engine(config.database_url)

    log.info("Starting DIP-bot")
    build_bot(config).run(config.discord_token)


if __name__ == "__main__":
    main()
