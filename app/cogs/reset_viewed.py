import discord
from discord.ext import commands

from app.utilities import text, database


class ResetViewed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.RESET_VIEWED_HELP)
    async def reset_viewed(self, ctx):
        await ctx.defer(ephemeral=True)
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        database.delete_seen_by_guild(guild_id)
        await ctx.respond(text.RESET_VIEWED_MESSAGE)


def setup(bot):
    bot.add_cog(ResetViewed(bot))
