import asyncio
import time
from datetime import datetime

from app.bot import image_sender
from app.utilities import database, constants, utility, text


class MainLoop:
    def __init__(self, parameters):
        self._ctx = parameters['ctx']
        self._guild_id = parameters['guild_id']
        self._restart = parameters['restart']
        self._channel_id = self._ctx.id

    async def run(self):
        while database.get_channel(self._channel_id):
            if not self._restart:
                sent = await self._send_images(database.get_posting_amount(self._channel_id))
                if not sent:
                    utility.log_event(f'Out of images for {self._guild_id}')
                    await self._ctx.send(text.NO_MORE_TO_SEE)
                    database.delete_channel(self._channel_id)
                    break
                else:
                    database.set_last_post_date(self._channel_id, time.time())
            self._restart = False
            await self._wait()
        utility.log_event(f'Stopped posting for server {self._guild_id} channel {self._channel_id}')

    async def _send_images(self, post_amount):
        sender = image_sender.ImageSender(self._ctx, self._guild_id)
        for _ in range(int(post_amount)):
            sent = await sender.send_image()
            if not sent:
                return False
        return True

    async def _wait(self):
        last_post_date = datetime.fromtimestamp(float(database.get_last_post_date(self._channel_id)))
        start_waiting = (datetime.now() - last_post_date).total_seconds()
        while start_waiting < (constants.TRIGGER_DURATION / int(database.get_posting_frequency(self._channel_id))):
            await asyncio.sleep(constants.POLL_INTERVAL)
            start_waiting += constants.POLL_INTERVAL
