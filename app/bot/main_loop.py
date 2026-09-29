"""The per-channel posting loop."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import discord
from discord.abc import Messageable

from app.bot.image_sender import ImageSender
from app.config import Config
from app.db import channels, session_scope
from app.utilities import text

log = logging.getLogger(__name__)


class MainLoop:
    """Posts to one channel on its schedule until the channel is deactivated."""

    def __init__(
        self,
        channel: Messageable,
        guild_id: int,
        *,
        restart: bool,
        config: Config,
    ) -> None:
        """
        :param channel: Where to post.
        :param guild_id: Posting scope; the user id when ``channel`` is a DM.
        :param restart: ``True`` when resuming an existing schedule, which skips the
            immediate post and waits for the next due time instead.
        :param config: Runtime configuration.
        """
        self._channel = channel
        self._guild_id = guild_id
        self._restart = restart
        self._config = config
        self._channel_id: int = channel.id
        self._sender = ImageSender(channel, guild_id, config)

    async def run(self) -> None:
        """Post, wait, repeat, until the channel goes inactive or the library empties."""
        log.info("Posting loop started for guild %s channel %s", self._guild_id, self._channel_id)
        try:
            while True:
                schedule = await self._schedule()
                if schedule is None:
                    break

                if not self._restart and not await self._post(schedule.post_amount):
                    break
                self._restart = False

                if not await self._wait():
                    break
        except asyncio.CancelledError:
            log.info("Posting loop cancelled for channel %s", self._channel_id)
            raise
        finally:
            log.info("Posting loop stopped for guild %s channel %s", self._guild_id, self._channel_id)

    async def _schedule(self) -> channels.Schedule | None:
        """The channel's current schedule, or ``None`` if it should stop posting.

        One query per tick instead of the old three (§2.5).
        """
        async with session_scope() as session:
            schedule = await channels.get_schedule(session, self._channel_id)
        if schedule is None or not schedule.active:
            return None
        return schedule

    async def _post(self, amount: int) -> bool:
        """Send one batch and record the time.

        :return: ``False`` when the loop should stop.
        """
        try:
            sent = await self._sender.send_batch(amount)
        except discord.Forbidden:
            log.warning("Lost permission to post in channel %s, deactivating", self._channel_id)
            await self._deactivate()
            return False

        if sent == 0:
            await self._channel.send(text.NO_MORE_TO_SEE)
            await self._deactivate()
            return False

        async with session_scope() as session:
            await channels.set_last_post(session, self._channel_id, datetime.now())
        return True

    async def _wait(self) -> bool:
        """Sleep until the next post is due.

        Wakes at the earlier of "post is due" and one poll interval, so a change made
        with ``/posts change_frequency`` or ``/stop`` is picked up promptly while an
        idle channel still lands its post on time rather than up to a poll late.

        :return: ``False`` if the channel went inactive while waiting.
        """
        poll_seconds = self._config.poll_interval.total_seconds()
        while True:
            schedule = await self._schedule()
            if schedule is None:
                return False

            due_at = schedule.last_post + self._config.post_interval(schedule.post_frequency)
            remaining = (due_at - datetime.now()).total_seconds()
            if remaining <= 0:
                return True
            await asyncio.sleep(min(remaining, poll_seconds))

    async def _deactivate(self) -> None:
        async with session_scope() as session:
            await channels.deactivate(session, self._channel_id)
