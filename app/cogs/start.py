import discord
from discord import ApplicationContext
from discord.ext import commands

from app.commands.start_posting import StartPosting
from app.utilities import text, utility


class Start(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    @discord.command(description=text.START_POSTING_HELP)
    async def start(self,
                    ctx: ApplicationContext,
                    amount: discord.Option(int, choices=[1, 2, 3, 4, 5], description=text.POST_AMOUNT_HELP),
                    frequency: discord.Option(int, choices=[1, 2, 3, 4, 5], description=text.CHANGE_FREQUENCY_HELP)) -> None:
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        start_command = StartPosting(ctx, amount, frequency)
        await start_command.run()


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Start(bot))
