import discord
from discord.ext import commands

from app.utilities import text, utility


class HealthCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.HEALTH_CHECK_HELP)
    async def health_check(self, ctx):
        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            await ctx.respond(text.HEALTH_CHECK_RESPONSE)


def setup(bot):
    bot.add_cog(HealthCheck(bot))
