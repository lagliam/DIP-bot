import discord
from discord import ApplicationContext
from discord.ext import commands

from app.utilities import text, database, utility


class Stop(commands.Cog):
    """
    Class that represents a Stop
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        :type bot: discord.Bot
        """

        self.bot = bot

    @discord.command(description=text.STOP_POSTING_HELP)
    async def stop(self, ctx: ApplicationContext) -> None:
        """
        Stops posting in the channel the command was called in

        :param ctx:The context object
        :type ctx: ApplicationContext
        """

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
