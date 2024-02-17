import discord
from discord.ext import commands

from app.utilities import text, database, constants


class GetTopLiked(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.TOP_LIKED_HELP)
    async def get_top_liked(self, ctx):
        await ctx.defer(ephemeral=True)
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        filename = database.get_top_liked_file(guild_id, ctx.channel.id)
        await ctx.respond('', file=discord.File(constants.IMAGES_PATH + filename))


def setup(bot):
    bot.add_cog(GetTopLiked(bot))
