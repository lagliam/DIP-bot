import discord
from discord.ext import commands

from app.utilities import text, utility, database


class ResetLastViewed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.RESET_LAST_VIEWED_HELP)
    async def reset_last_viewed(self, ctx):
        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            database.reset_last_viewed_for_channel(ctx.channel.id)
            await ctx.respond(text.RESET_LAST_VIEWED_RESPONSE)


def setup(bot):
    bot.add_cog(ResetLastViewed(bot))
