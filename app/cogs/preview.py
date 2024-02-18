import discord
from discord.ext import commands

from app.utilities import text, constants, utility


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


def get_image_filename():
    images_list = utility.image_list(constants.IMAGES_PATH)
    if len(images_list) == 0:
        utility.log_event('No images in directory')
        return None
    filename = utility.get_file(images_list)
    return filename


class Preview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.command(description=text.PREVIEW_HELP)
    async def preview(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await utility.check_permissions(ctx, self.bot):
            return
        filename = get_image_filename()
        if not filename:
            await ctx.respond('No images to preview')
        else:
            await ctx.respond(view=PreviewView(), file=discord.File(constants.IMAGES_PATH + filename))


def setup(bot):
    bot.add_cog(Preview(bot))
