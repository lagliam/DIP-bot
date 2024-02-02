import discord
from discord.ext import commands

from app.bot.image_sender import ImageSender
from app.utilities import text, utility


class GetOneImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.GET_IMAGE_HELP)
    async def get_one_image(self, ctx):
        await ctx.defer(ephemeral=True)
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        image_sender = ImageSender(ctx.channel, guild_id)
        await ctx.respond(text.START_POSTING)
        sent = await image_sender.send_image()
        if not sent:
            utility.log_event(f'Unable to send images for {guild_id}')
            await ctx.send(text.NO_MORE_TO_SEE)


def setup(bot):
    bot.add_cog(GetOneImage(bot))
