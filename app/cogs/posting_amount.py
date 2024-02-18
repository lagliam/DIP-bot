import discord
from discord.ext import commands

from app.utilities import text, database, utility


class PostingAmount(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.POST_AMOUNT_HELP)
    async def posting_amount(self, ctx, amount: discord.Option(int, choices=[1, 2, 3, 4, 5])):
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        database.set_post_amount(ctx.channel.id, amount)
        await ctx.respond(text.POST_AMOUNT_END)


def setup(bot):
    bot.add_cog(PostingAmount(bot))
