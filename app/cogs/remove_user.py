import discord
from discord.ext import commands

from app.utilities import text, database, utility


class RemoveUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.REMOVE_USER_HELP)
    @discord.guild_only()
    async def remove_user(self, ctx, user: discord.Member):
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if user.id == ctx.guild.owner:
            await ctx.respond('Unable to remove the guild owner from bot permissions')
            return
        database.remove_user(user.id, ctx.guild.id)
        await ctx.respond(text.REMOVE_USER_RESPONSE)


def setup(bot):
    bot.add_cog(RemoveUser(bot))
