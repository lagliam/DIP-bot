"""Owns the per-channel posting tasks.

Replaces the old ``app.App``, which gathered a list of coroutines once at startup and
had no way to add a channel afterwards — ``/start`` instead did
``await asyncio.create_task(loop.run())``, pinning the command handler for the life of
the loop (§1.3). Here the scheduler keeps a strong reference to every task, so loops
are not garbage-collected mid-flight and can be cancelled cleanly on shutdown.
"""

from __future__ import annotations

import asyncio
import logging

import discord
from discord.abc import Messageable

from app.bot.main_loop import MainLoop
from app.config import Config
from app.db import channels, session_scope

log = logging.getLogger(__name__)


class PostingScheduler:
    """Starts, tracks and stops one :class:`MainLoop` per channel."""

    def __init__(self, bot: discord.Bot, config: Config) -> None:
        self._bot = bot
        self._config = config
        self._tasks: dict[int, asyncio.Task[None]] = {}

    @property
    def running(self) -> int:
        """How many posting loops are currently alive."""
        return len(self._tasks)

    async def resume_all(self) -> int:
        """Restart a loop for every channel marked active in the database.

        :return: How many loops were started.
        """
        async with session_scope() as session:
            schedules = await channels.active_schedules(session)

        started = 0
        for schedule in schedules:
            try:
                channel = await self._bot.fetch_channel(schedule.channel_id)
            except (discord.NotFound, discord.Forbidden) as error:
                # The channel was deleted or the bot was kicked while it was down.
                log.warning(
                    "Cannot resume channel %s (%s), deactivating", schedule.channel_id, type(error).__name__
                )
                async with session_scope() as session:
                    await channels.deactivate(session, schedule.channel_id)
                continue

            self.start(channel, schedule.guild_id, restart=True)
            started += 1

        log.info("Resumed %d posting loop(s)", started)
        return started

    def start(self, channel: Messageable, guild_id: int, *, restart: bool) -> bool:
        """Start a posting loop for a channel unless one is already running.

        :param restart: ``True`` when resuming an existing schedule rather than
            responding to a fresh ``/start``.
        :return: ``True`` if a new loop was started.
        """
        channel_id: int = channel.id
        existing = self._tasks.get(channel_id)
        if existing is not None and not existing.done():
            log.debug("Posting loop already running for channel %s", channel_id)
            return False

        loop = MainLoop(channel, guild_id, restart=restart, config=self._config)
        task = asyncio.create_task(loop.run(), name=f"posting-loop-{channel_id}")
        self._tasks[channel_id] = task
        task.add_done_callback(self._on_task_done)
        return True

    def stop(self, channel_id: int) -> bool:
        """Cancel a channel's loop.

        The loop also notices deactivation on its next tick; cancelling makes ``/stop``
        take effect immediately rather than after up to one poll interval.

        :return: ``True`` if a running loop was cancelled.
        """
        task = self._tasks.get(channel_id)
        if task is None or task.done():
            return False
        task.cancel()
        return True

    async def shutdown(self) -> None:
        """Cancel every loop and wait for them to unwind."""
        tasks = list(self._tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()
        log.info("All posting loops stopped")

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        """Drop the finished task and surface any crash.

        Without this a loop that raised would fail silently, since nothing ever
        awaits these tasks.
        """
        for channel_id, tracked in list(self._tasks.items()):
            if tracked is task:
                del self._tasks[channel_id]
                break

        if task.cancelled():
            return
        error = task.exception()
        if error is not None:
            log.error("%s crashed", task.get_name(), exc_info=error)
