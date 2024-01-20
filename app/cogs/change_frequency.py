import discord
from discord.ext import commands

from app.utilities import text, database


class ChangeFrequency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.CHANGE_FREQUENCY_HELP)
    async def change_frequency(self, ctx, amount: discord.Option(int, choices=[1, 2, 3, 4, 5])):
        await ctx.defer(ephemeral=True)
        if not database.get_channel(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        if int(amount) > 5 or int(amount) < 0 or int(amount) == 0:
            await ctx.respond(text.CHANGE_FREQUENCY_ERROR)
            return
        database.set_post_frequency(ctx.channel.id, amount)
        await ctx.respond(text.CHANGE_FREQUENCY_END)


def setup(bot):
    bot.add_cog(ChangeFrequency(bot))
