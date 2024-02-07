import discord
from discord.ext import commands

from app.utilities import text, database


class PostingAmount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.POST_AMOUNT_HELP)
    async def posting_amount(self, ctx, amount: discord.Option(int, choices=[1, 2, 3, 4, 5])):
        await ctx.defer(ephemeral=True)
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        if int(amount) > 5 or int(amount) < 0 or int(amount) == 0:
            await ctx.respond(text.CHANGE_FREQUENCY_ERROR)
            return
        database.set_post_amount(ctx.channel.id, amount)
        await ctx.respond(text.POST_AMOUNT_END)


def setup(bot):
    bot.add_cog(PostingAmount(bot))
