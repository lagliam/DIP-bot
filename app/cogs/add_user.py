import discord
from discord.ext import commands

from app.utilities import text, database, utility


class AddUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.ADD_USER_HELP)
    @discord.guild_only()
    async def add_user(self, ctx, user: discord.Member):
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        database.add_user(user.id, user.name, ctx.guild.id)
        await ctx.respond(text.ADD_USER_RESPONSE)


def setup(bot):
    bot.add_cog(AddUser(bot))
