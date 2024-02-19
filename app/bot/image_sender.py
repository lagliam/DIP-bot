import discord
from discord import TextChannel, PartialMessageable

from app.utilities import constants, utility, database


class ImageSender:
    def __init__(self, ctx: TextChannel | PartialMessageable, guild_id: int) -> None:
        self._ctx = ctx
        self._guild_id = guild_id
        self._channel_id = self._ctx.id

    async def send_image(self) -> bool:
        filename = self._get_image()
        if not filename:
            return False
        else:
            return await self._send(filename)

    def _get_image(self) -> str | None:
        file_list = utility.image_list(constants.IMAGES_PATH)
        if len(file_list) == 0:
            utility.log_event('No images in directory')
            return None
        return self._get_unseen_image(file_list)

    def _get_unseen_image(self, file_list: list) -> str | None:
        filename = utility.get_file(file_list)
        if not filename:
            return filename
        is_seen = database.is_image_seen(filename, self._guild_id)
        while is_seen:
            try:
                filename = utility.get_file(file_list)
            except ValueError:
                utility.log_event(f'No unseen images for guild {self._guild_id}')
                filename = None
                break
            is_seen = database.is_image_seen(filename, self._guild_id)
        return filename

    async def _send(self, filename: str) -> bool:
        await self._ctx.send('', file=discord.File(constants.IMAGES_PATH + filename))
        database.write_viewed_image_list_for_guild(filename, self._guild_id)
        return True
