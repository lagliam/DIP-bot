import discord
from discord import ApplicationContext
from discord.ext import commands

from app.bot.image_sender import ImageSender
from app.utilities import text, database, utility, constants


class PreviewView(discord.ui.View):
    @discord.ui.button(label='Preview More', style=discord.ButtonStyle.primary, emoji='😎')
    async def button_callback(self, button, interaction):
        button.disabled = True
        button.label = 'End Of Preview'
        button.emoji = None
        image1 = get_image_filename()
        image2 = get_image_filename()
        image3 = get_image_filename()
        await interaction.response.edit_message(view=self, files=[discord.File(constants.IMAGES_PATH + image1),
                                                                  discord.File(constants.IMAGES_PATH + image2),
                                                                  discord.File(constants.IMAGES_PATH + image3)])


def get_image_filename() -> str | None:
    images_list = utility.image_list(constants.IMAGES_PATH)
    if len(images_list) == 0:
        utility.log_event('No images in directory')
        return None
    filename = utility.get_file(images_list)
    return filename


class ImageCommands(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot

    image_commands = discord.SlashCommandGroup('images', 'Part of the images features')

    @image_commands.command(description=text.GET_IMAGE_HELP)
    async def get_one_image(self, ctx: ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        image_sender = ImageSender(ctx.channel, guild_id)
        await ctx.respond(text.GET_IMAGE)
        sent = await image_sender.send_image()
        if not sent:
            utility.log_event(f'Unable to send image to channel {ctx.channel.id}')
            await ctx.send(text.NO_MORE_TO_SEE)
            if not database.is_channel_deleted(ctx.channel.id):
                database.delete_channel(ctx.channel.id)

    @image_commands.command(description=text.PREVIEW_HELP)
    async def preview(self, ctx: ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        filename = get_image_filename()
        if not filename:
            await ctx.respond('No images to preview')
        else:
            await ctx.respond(view=PreviewView(), file=discord.File(constants.IMAGES_PATH + filename))

    @image_commands.command(description=text.TOP_LIKED_HELP)
    async def get_top_liked(self, ctx: ApplicationContext) -> None:
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        if ctx.channel.type.name == 'private':
            guild_id = ctx.user.id
        else:
            guild_id = ctx.channel.guild.id
        filename = database.get_top_liked_file(guild_id, ctx.channel.id)
        await ctx.respond('', file=discord.File(constants.IMAGES_PATH + filename))


def setup(bot: discord.Bot) -> None:
    bot.add_cog(ImageCommands(bot))
