import discord
from discord import ApplicationContext, NotFound
from discord.ext import commands

from app.commands.report import Report
from app.utilities import text, utility, database


class AdminCommands(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', 'Part of the admin features')

    @admin.command(description=text.HEALTH_CHECK_HELP)
    async def health_check(self, ctx: ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        if await utility.check_permissions(ctx, self.bot):
            await ctx.respond(text.HEALTH_CHECK_RESPONSE)

    @admin.command(description=text.ADD_USER_HELP)
    async def add_user(self, ctx: ApplicationContext, user: discord.Member) -> None:
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
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            await ctx.defer(ephemeral=True)
            await ctx.respond(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}s')


def setup(bot: discord.Bot) -> None:
    bot.add_cog(AdminCommands(bot))
