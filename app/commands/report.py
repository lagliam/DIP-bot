import datetime

import discord

from app.utilities import database


class Report:
    def __init__(self, message: discord.Message):
        self.message = message

    async def log(self) -> bool:
        if self.message.guild is None:
            guild = None
        else:
            guild = self.message.guild.id
        database.log_report(self.message.channel.id, guild, self.message.attachments[0].filename)
        get_report_count = database.get_report_count(
            self.message.channel.id, guild, self.message.attachments[0].filename)
        if get_report_count > 5:
            await self.save_image_for_review(self.message.channel.id)
        return True

    async def save_image_for_review(self, channel_id: int) -> None:
        file = ('reported_images/' + str(channel_id) + '-'
                + datetime.datetime.now().strftime('%Y-%m-%d') + '-' + self.message.attachments[0].filename)
        await self.message.attachments[0].save(file)
