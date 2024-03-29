from datetime import datetime

import discord
from discord import ApplicationContext
from discord.ext import commands

from app.utilities import text, database, constants, utility


class PostingCommands(commands.Cog):
    """
    Class representing a PostingCommands

    Attributes
    ----------
    posting_commands : discord.SlashCommandGroup
        The slash command group to group commands under the 'posts' slash command
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        :type bot: discord.Bot
        """

        self.bot = bot

    posting_commands = discord.SlashCommandGroup('posts', 'Part of the image posting features')

    @posting_commands.command(description=text.NEXT_POST_DETAILS_HELP)
    async def next_post_details(self, ctx: ApplicationContext) -> None:
        """
        Gets how long until the next post and sends it

        :param ctx: The context object
        :type ctx: ApplicationContext
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        last_post_date = datetime.fromtimestamp(float(database.get_last_post_date(ctx.channel.id)))
        seconds_since_last_post = (datetime.now() - last_post_date).total_seconds()
        trigger_time = constants.TRIGGER_DURATION / int(database.get_posting_frequency(ctx.channel.id))
        minutes_to_next_post = (trigger_time - seconds_since_last_post) / 60
        post_amount = int(database.get_posting_amount(ctx.channel.id))
        await ctx.respond(f'The next post of {post_amount} image(s) will be in {int(minutes_to_next_post)} minutes')

    @posting_commands.command(description=text.POST_AMOUNT_HELP)
    async def posting_amount(self, ctx: ApplicationContext, amount: discord.Option(int, choices=[1, 2, 3, 4, 5])) -> None:
        """
        Sets the amount of images to send at the same time

        :param ctx: The context object
        :type ctx: ApplicationContext
        :param amount: Amount between 1 and 5 to post
        :type amount: discord.Option
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        database.set_post_amount(ctx.channel.id, amount)
        await ctx.respond(text.POST_AMOUNT_END)

    @posting_commands.command(description=text.RESET_LAST_VIEWED_HELP)
    async def reset_last_viewed(self, ctx: ApplicationContext) -> None:
        """
        Resets the time for when the last image was sent

        :param ctx: The context object
        :type ctx: ApplicationContext
        """

        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            database.reset_last_viewed_for_channel(ctx.channel.id)
            await ctx.respond(text.RESET_LAST_VIEWED_RESPONSE)

    @posting_commands.command(description=text.RESET_VIEWED_HELP)
    async def reset_viewed(self, ctx: ApplicationContext) -> None:
        """
        Resets the images that have been viewed so that they can be sent again

        :param ctx: The context object
        :type ctx: ApplicationContext
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        database.delete_seen_by_guild(guild_id)
        await ctx.respond(text.RESET_VIEWED_MESSAGE)

    @posting_commands.command(description=text.STATS_HELP)
    async def stats(self, ctx: ApplicationContext) -> None:
        """
        Gets bot stats for the server

        :param ctx: The context object
        :type ctx: ApplicationContext
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
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
            color=discord.Colour.blurple(),
        )
        embed.add_field(name='Total images sent', value=f'Sent: {post_total}')
        embed.add_field(name='Channels being posted to', value=channels_names_string)
        await ctx.respond('', embed=embed)

    @posting_commands.command(description=text.CHANGE_FREQUENCY_HELP)
    async def change_frequency(self, ctx: ApplicationContext, amount: discord.Option(int, choices=[1, 2, 3, 4, 5])) -> None:
        """
        Changes the daily frequency of posts sent to the server

        :param ctx:The context object
        :type ctx: ApplicationContext
        :param amount: The number of posts per day between 1 and 5
        :type amount: int
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if database.is_channel_deleted(ctx.channel.id):
            await ctx.respond(text.POSTING_NOT_STARTED)
            return
        database.set_post_frequency(ctx.channel.id, amount)
        await ctx.respond(text.CHANGE_FREQUENCY_END)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(PostingCommands(bot))
