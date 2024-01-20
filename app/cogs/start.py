import discord
from discord.ext import commands

from app.commands.start_posting import StartPosting
from app.utilities import text


class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.START_POSTING_HELP)
    async def start(self, ctx):
        await ctx.defer(ephemeral=True)
        start_command = StartPosting(ctx)
        await start_command.run()


def setup(bot):
    bot.add_cog(Start(bot))
