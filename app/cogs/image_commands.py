"""The ``/images`` command group."""

from __future__ import annotations

import asyncio
import logging
import random

import discord
from discord import ApplicationContext
from discord.ext import commands

from app.bot.client import DipBot
from app.bot.image_sender import ImageSender
from app.config import Config
from app.db import channels, reactions, session_scope
from app.utilities import imaging, text
from app.utilities.discord_utils import check_permissions, scope_id

log = logging.getLogger(__name__)

_PREVIEW_COUNT = 3


async def preview_files(config: Config, count: int) -> list[discord.File]:
    """Pick up to ``count`` random images from the library to show as a preview."""
    library = await asyncio.to_thread(imaging.image_files, config.images_path)
    if not library:
        log.info("Preview requested but %s is empty", config.images_path)
        return []
    chosen = random.sample(library, k=min(count, len(library)))
    return [discord.File(path) for path in chosen]


class PreviewView(discord.ui.View):
    """A one-shot button that reveals a few more images."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

    @discord.ui.button(label="Preview More", style=discord.ButtonStyle.primary, emoji="😎")
    async def button_callback(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """Replace the message with another handful of images and disable the button."""
        button.disabled = True
        button.label = "End Of Preview"
        button.emoji = None
        files = await preview_files(self._config, _PREVIEW_COUNT)
        await interaction.response.edit_message(view=self, files=files)


class ImageCommands(commands.Cog):
    """Commands that fetch individual images on demand."""

    def __init__(self, bot: DipBot) -> None:
        self.bot = bot

    image_commands = discord.SlashCommandGroup("images", "Part of the images features")

    @image_commands.command(description=text.GET_IMAGE_HELP)
    async def get_one_image(self, ctx: ApplicationContext) -> None:
        """Post a single unseen image immediately."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        sender = ImageSender(ctx.channel, scope_id(ctx), self.bot.config)

        if await sender.send_one():
            await ctx.respond(text.GET_IMAGE)
            return

        log.info("Nothing left to send to channel %s", ctx.channel.id)
        await ctx.respond(text.NO_MORE_TO_SEE)
        async with session_scope() as session:
            if await channels.is_active(session, ctx.channel.id):
                await channels.deactivate(session, ctx.channel.id)
                self.bot.scheduler.stop(ctx.channel.id)

    @image_commands.command(description=text.PREVIEW_HELP)
    async def preview(self, ctx: ApplicationContext) -> None:
        """Show what the bot has to post, without marking anything as seen."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        files = await preview_files(self.bot.config, 1)
        if not files:
            await ctx.respond(text.NO_IMAGES_TO_PREVIEW)
            return
        await ctx.respond(view=PreviewView(self.bot.config), file=files[0])

    @image_commands.command(description=text.TOP_LIKED_HELP)
    async def get_top_liked(self, ctx: ApplicationContext) -> None:
        """Post the most-reacted-to image for this channel."""
        await ctx.defer(ephemeral=True)
        if not await check_permissions(ctx, self.bot):
            return

        async with session_scope() as session:
            filename = await reactions.top_liked_filename(session, scope_id(ctx), ctx.channel.id)

        # An empty result is now a message rather than an IndexError (§1.2).
        if filename is None:
            await ctx.respond(text.NO_LIKED_IMAGES)
            return

        path = self.bot.config.images_path / filename
        if not path.is_file():
            log.warning("Top liked image %s is no longer on disk", filename)
            await ctx.respond(text.LIKED_IMAGE_MISSING)
            return
        await ctx.respond(file=discord.File(path))


def setup(bot: DipBot) -> None:
    bot.add_cog(ImageCommands(bot))
