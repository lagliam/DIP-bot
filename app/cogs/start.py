import discord
from discord import ApplicationContext
from discord.ext import commands

from app.commands.start_posting import StartPosting
from app.utilities import text, utility


class Start(commands.Cog):
    """
    Class that represents a Start
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        :type bot: discord.Bot
        """

        self.bot = bot

    @discord.command(description=text.START_POSTING_HELP)
    async def start(self,
                    ctx: ApplicationContext,
                    amount: discord.Option(int, choices=[1, 2, 3, 4, 5], description=text.POST_AMOUNT_HELP),
                    frequency: discord.Option(int, choices=[1, 2, 3, 4, 5], description=text.CHANGE_FREQUENCY_HELP)
                    ) -> None:
        """
        Starts posting to the channel the command was called from

        :param ctx:The context object
        :type ctx: ApplicationContext
        :param amount: Amount of posts to send between 1 and 5
        :type amount: int
        :param frequency:The amount of times per day to send posts between 1 and 5
        :type frequency: int
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        start_command = StartPosting(ctx, amount, frequency)
        await start_command.run()


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Start(bot))
