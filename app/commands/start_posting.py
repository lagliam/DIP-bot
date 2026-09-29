"""The ``/start`` command's logic."""

from __future__ import annotations

import logging

from discord import ApplicationContext

from app.bot.scheduler import PostingScheduler
from app.db import channels, session_scope
from app.utilities import text
from app.utilities.discord_utils import scope_id

log = logging.getLogger(__name__)


class StartPosting:
    """Registers a channel and hands its loop to the scheduler."""

    def __init__(
        self,
        ctx: ApplicationContext,
        amount: int,
        frequency: int,
        scheduler: PostingScheduler,
    ) -> None:
        """
        :param ctx: The invoking context.
        :param amount: Images per post.
        :param frequency: Posts per window.
        :param scheduler: Owns the resulting task
        """
        self._ctx = ctx
        self._amount = amount
        self._frequency = frequency
        self._scheduler = scheduler
        self._channel_id = ctx.channel.id
        self._guild_id = scope_id(ctx)

    async def run(self) -> None:
        """Start posting or explain why it is already running."""
        async with session_scope() as session:
            if await channels.is_active(session, self._channel_id):
                await self._ctx.respond(text.START_POSTING_REPEAT)
                return
            is_new = await channels.start(
                session,
                self._channel_id,
                self._guild_id,
                post_amount=self._amount,
                post_frequency=self._frequency,
            )

        log.info(
            "%s posting for guild %s channel %s",
            "Started" if is_new else "Restarted",
            self._guild_id,
            self._channel_id,
        )
        await self._ctx.respond(text.START_POSTING if is_new else text.RESTART_POSTING)
        self._scheduler.start(self._ctx.channel, self._guild_id, restart=not is_new)
