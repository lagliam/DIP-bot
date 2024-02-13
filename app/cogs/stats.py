import discord
from discord.ext import commands

from app.utilities import text, database, utility


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.STATS_HELP)
    async def stats(self, ctx):
        await ctx.defer(ephemeral=True)
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
            guild_name = 'Private Messages'
            channels_names_string = 'DM Channel'
        else:
            guild_id = ctx.channel.guild.id
            guild_name = ctx.channel.guild.name
            channels = database.channels_posting_to_per_guild(guild_id)
            channels_names_list = []
            for t in channels:
                channel = await self.bot.fetch_channel(t[0])
                channels_names_list.append(channel.name)
            channels_names_string = ', '.join(channels_names_list)
        post_total = database.total_images_sent_to_guild(guild_id)
        embed = discord.Embed(
            title=f'Bot Stats for {guild_name}',
            description=text.STATS_HELP,
            color=discord.Colour.blurple(),  # Pycord provides a class with default colors you can choose from
        )
        embed.add_field(name='Total images sent', value=f'Sent: {post_total}')
        embed.add_field(name='Channels being posted to', value=channels_names_string)
        await ctx.respond('', embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
