import discord
from discord import ApplicationContext
from discord.ext import commands

from app.utilities import text, database, utility


class Stop(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @discord.command(description=text.STOP_POSTING_HELP)
    async def stop(self, ctx: ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.STOP_POSTING_REPEAT)
            return
        utility.log_event(f'Stop posting called for channel {ctx.channel.id}')
        database.delete_channel(ctx.channel.id)
        await ctx.respond(text.STOP_POSTING)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Stop(bot))
