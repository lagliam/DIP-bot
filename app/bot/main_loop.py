import asyncio
import time
from datetime import datetime

import discord.channel

from app.bot import image_sender
from app.utilities import database, constants, utility, text


class MainLoop:
    def __init__(self, parameters: dict) -> None:
        self._ctx: any = parameters['ctx']
        self._guild_id: int = parameters['guild_id']
        self._restart: bool = parameters['restart']
        self._channel_id: int = self._ctx.id

    async def run(self) -> None:
        while not database.is_channel_deleted(self._channel_id):
            if not self._restart:
                sent = await self._send_images(database.get_posting_amount(self._channel_id))
                if not sent:
                    await self._ctx.send(text.NO_MORE_TO_SEE)
                    database.delete_channel(self._channel_id)
                    break
                else:
                    database.set_last_post_date(self._channel_id, time.time())
            self._restart = False
            await self._wait()
        utility.log_event(f'Stopped posting for guild {self._guild_id} channel {self._channel_id}')

    async def _send_images(self, post_amount: int) -> bool:
        sender = image_sender.ImageSender(self._ctx, self._guild_id)
        for _ in range(int(post_amount)):
            sent = await sender.send_image()
            if not sent:
                return False
        return True

    async def _wait(self) -> None:
        while self._start_waiting() < (self._trigger_time()) and not database.is_channel_deleted(self._channel_id):
            await asyncio.sleep(constants.POLL_INTERVAL)

    def _trigger_time(self) -> float:
        try:
            posting_freq = int(database.get_posting_frequency(self._channel_id))
        except TypeError:
            return 1
        return constants.TRIGGER_DURATION / posting_freq

    def _start_waiting(self) -> float:
        last_post_date = datetime.fromtimestamp(float(database.get_last_post_date(self._channel_id)))
        return (datetime.now() - last_post_date).total_seconds()
