from datetime import datetime

import discord
from discord.ext import commands

from app.utilities import text, database, constants


class NextPostDetails(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.NEXT_POST_DETAILS_HELP)
    async def next_post_details(self, ctx):
        await ctx.defer(ephemeral=True)
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        last_post_date = datetime.fromtimestamp(float(database.get_last_post_date(ctx.channel.id)))
        seconds_since_last_post = (datetime.now() - last_post_date).total_seconds()
        trigger_time = constants.TRIGGER_DURATION / int(database.get_posting_frequency(ctx.channel.id))
        minutes_to_next_post = (trigger_time - seconds_since_last_post) / 60
        post_amount = int(database.get_posting_amount(ctx.channel.id))
        await ctx.respond(f'The next post of {post_amount} image(s) will be in {int(minutes_to_next_post)} minutes')


def setup(bot):
    bot.add_cog(NextPostDetails(bot))
