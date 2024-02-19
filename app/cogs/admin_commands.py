import discord
from discord import ApplicationContext, NotFound
from discord.ext import commands

from app.commands.report import Report
from app.utilities import text, utility, database


class AdminCommands(commands.Cog):
    """
    Class used to represent the AdminCommands

    Attributes
    ----------
    admin : discord.SlashCommandGroup
        The slash command group to group commands under the 'admin' slash command
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        :type bot: discord.Bot
        """

        self.bot = bot

    admin = discord.SlashCommandGroup('admin', 'Part of the admin features')

    @admin.command(description=text.HEALTH_CHECK_HELP)
    async def health_check(self, ctx: ApplicationContext) -> None:
        """
        Checks that the bot is alive and responding to commands

        :param ctx: The context object
        :type ctx: ApplicationContext
        """
        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            await ctx.respond(text.HEALTH_CHECK_RESPONSE)

    @admin.command(description=text.ADD_USER_HELP)
    async def add_user(self, ctx: ApplicationContext, user: discord.Member) -> None:
        """
        Adds a user to the database that is authorized to execute bot commands in the server

        :param ctx: The context object
        :type ctx: ApplicationContext
        :param user: The user to add
        :type user: discord.Member
        """

        await ctx.defer(ephemeral=True)
        if utility.is_private_channel(ctx):
            await ctx.respond(text.DENY_PRIVATE_MESSAGES)
            return
        if not await utility.check_permissions(ctx, self.bot):
            return
        database.add_user(user.id, user.name, ctx.guild.id)
        await ctx.respond(text.ADD_USER_RESPONSE)

    @admin.command(description=text.REMOVE_USER_HELP)
    async def remove_user(self, ctx: ApplicationContext, user: discord.Member) -> None:
        """

        Removes a user from the database that is authorized to execute bot commands in the server

        :param ctx: The context object
        :type ctx: ApplicationContext
        :param user: The user to remove
        :type user: discord.Member
        """

        await ctx.defer(ephemeral=True)
        if utility.is_private_channel(ctx):
            await ctx.respond(text.DENY_PRIVATE_MESSAGES)
            return
        if not await utility.check_permissions(ctx, self.bot):
            return
        if user.id == ctx.guild.owner:
            await ctx.respond('Unable to remove the guild owner from bot permissions')
            return
        database.remove_user(user.id, ctx.guild.id)
        await ctx.respond(text.REMOVE_USER_RESPONSE)

    @admin.command(description=text.REPORT_HELP)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def report(self, ctx: ApplicationContext, message_id: str) -> None:
        """
        Reports an image to the bot owner for review and logs to the database

        :param ctx: The context object
        :type ctx: ApplicationContext
        :param message_id: The id of the message to report
        :type message_id: str
        """

        await ctx.defer(ephemeral=True)
        try:
            message = await ctx.fetch_message(int(message_id))
        except NotFound:
            await ctx.respond(text.REPORT_UNABLE_TO_FIND)
            return
        if message.author == self.bot.user:
            report = Report(message)
            status = await report.log()
            if status:
                await ctx.respond(text.REPORT_SENT)
            else:
                await ctx.respond(text.REPORT_FAILED)
        else:
            await ctx.respond(text.REPORT_NOT_A_BOT_MESSAGE)

    @report.error
    async def on_command_error(self, ctx: ApplicationContext, error):
        """
        Handles the cooldown of the report command

        :param ctx: The context object
        :type ctx: ApplicationContext
        :param error: The error object to check
        :type error: discord.CommandError
        """

        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.respond(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}s')


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AdminCommands(bot))
