import discord
from discord import ApplicationContext
from discord.ext import commands

from app.utilities import text, utility


class Help(commands.Cog):
    """
    Class used to represent a Help
    """

    def __init__(self, bot: discord.Bot) -> None:
        """
        Parameters
        ----------
        :param bot: The bot object
        :type bot: discord.Bot
        """

        self.bot = bot

    @discord.command(description=text.HELP_HELP)
    async def help(self, ctx: ApplicationContext) -> None:
        """
        Displays a help message with info on the bot

        :param ctx: The context object
        :type ctx: ApplicationContext
        """

        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        bot_info = (f'{self.bot.user.name} is a versatile Discord bot designed to enhance your server\'s visual '
                    f'experience by automatically posting images at predefined intervals. Whether you\'re looking to '
                    f'showcase artwork, memes, or any other visual content, the bot makes it easy to keep your server '
                    f'engaged with fresh and exciting images.')
        embed = discord.Embed(
            title=self.bot.user.name,
            description=bot_info,
            color=discord.Colour.blurple(),
        )
        popular_commands = (f'/start - Starts posting to a server on a daily interval\n'
                            f'/stop - Stops posting\n'
                            f'/get_one_image - Gets an image and posts it immediately')
        embed.add_field(name='Popular Commands', value=popular_commands)
        await ctx.respond('', embed=embed)


def setup(bot: discord.Bot) -> None:
    bot.add_cog(Help(bot))
