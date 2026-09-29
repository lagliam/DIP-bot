import discord
from discord import ApplicationContext, Option
from discord.ext import commands

from app.bot.client import DipBot
from app.commands.start_posting import StartPosting
from app.utilities import text
from app.utilities.discord_utils import check_permissions


class Start(commands.Cog):
    """Begins scheduled posting in a channel."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    @discord.command(description=text.START_POSTING_HELP)
    async def start(
        self,
        ctx: ApplicationContext,
        amount: Option(  # type: ignore[valid-type]
            int, choices=[1, 2, 3, 4, 5], description=text.POST_AMOUNT_HELP, default=1
        ),
        frequency: Option(  # type: ignore[valid-type]
            int, choices=[1, 2, 3, 4, 5], description=text.CHANGE_FREQUENCY_HELP, default=1
        ),
    ) -> None:
        """Start posting to the channel this was called from.

        :param ctx: The context of the command.
        :param amount: Images per post, 1-5.
        :param frequency: Posts per day, 1-5.
        """

        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return
        await StartPosting(ctx, amount, frequency, self.bot.scheduler).run()


def setup(bot: DipBot) -> None:
    bot.add_cog(Start(bot))
