import discord
from discord.ext import commands

from app.utilities import text, utility, database


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', 'Part of the admin features')

    @admin.command(description=text.HEALTH_CHECK_HELP)
    async def health_check(self, ctx):
        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            await ctx.respond(text.HEALTH_CHECK_RESPONSE)

    @admin.command(description=text.ADD_USER_HELP)
    @discord.guild_only()
    async def add_user(self, ctx, user: discord.Member):
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        database.add_user(user.id, user.name, ctx.guild.id)
        await ctx.respond(text.ADD_USER_RESPONSE)

    @admin.command(description=text.REMOVE_USER_HELP)
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
    bot.add_cog(AdminCommands(bot))
