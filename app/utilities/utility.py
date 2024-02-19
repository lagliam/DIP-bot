"""Contains the utility functions of the project"""

import logging
import os
import random

from pathlib import Path

import discord
from PIL import Image
from discord import ApplicationContext

from app.utilities import constants, database, text


def get_cogs() -> list:
    """
    Gets the command cots as a list

    :return: List of command cogs
    :rtype: list
    """

    directory_contents = os.listdir('app/cogs')
    cogs = []
    for content in directory_contents:
        if os.path.isfile('app/cogs/' + content):
            cogs.append(content.split('.')[0])
    return cogs


def image_list(directory: str) -> list[str]:
    """
    Gets a list of images from a source

    :param directory: Where to check
    :type directory: str
    :return: List of images in a source
    :rtype: list
    """

    images = []
    for filename in os.listdir(directory):
        if (filename.lower().endswith(".jpg")
                or filename.lower().endswith(".png")
                or filename.lower().endswith(".gif")
                or filename.lower().endswith(".jpeg")):
            images.append(filename)
            continue
        else:
            continue
    return images


def log_event(message: str) -> None:
    """
    Logger

    :param message: The message to log
    :type message: str
    """

    logging.basicConfig(
        handlers=[logging.FileHandler('log/dip-bot.log'), logging.StreamHandler()],
        format='%(asctime)s - %(message)s',
        level=logging.INFO
    )
    logging.info(message)


def get_file(file_list: list) -> str | None:
    """
    Gets a random file from a list

    :param file_list: List of files to pull from to send
    :type file_list: list
    :return: The file name to send or None if unable to get a file
    :rtype: str | None
    """

    filename = file_list.pop(random.randrange(len(file_list)))
    while is_large_file(constants.IMAGES_PATH + filename):
        log_event(f'Image {filename} too large to send, attempting to compress')
        try:
            compress_under_size(constants.LIMIT_SIZE, constants.IMAGES_PATH + filename)
        except ValueError:
            try:
                filename = file_list.pop(random.randrange(len(file_list)))
            except ValueError:
                log_event('All files remaining are too big to send')
                filename = None
                break
    return filename


def is_large_file(filepath: str) -> bool:
    """
    Determines if a file is too large to send

    :param filepath: Path to the file
    :type filepath: str
    :return: True if too large, False otherwise
    :rtype: bool
    """

    return os.path.getsize(filepath) > constants.LIMIT_SIZE


def compress_under_size(size: int, file_path: str) -> None:
    """
    Attempts to compress an image by reducing its quality until it is under the file limit size

    :param size: The limit size
    :type size: int
    :param file_path: Path to the file
    :type file_path: str
    """

    if Path(file_path).suffix == '.png':
        log_event(f'Cannot reduce file size of PNGs, skipping {file_path}')
        raise ValueError('File cannot be reduced')
    quality = 90
    current_size = os.path.getsize(file_path)
    while current_size > size or quality == 0:
        if quality == 0:
            log_event(f"File cannot be compressed below this size: {current_size}")
            raise ValueError('File cannot be reduced')
        compress_pic(file_path, quality)
        current_size = os.path.getsize(file_path)
        quality -= 45


def compress_pic(file_path: str, quality: int) -> None:
    """
    Compresses an image

    :param file_path: Path to file
    :type file_path: str
    :param quality: The quality to save the image as
    :type quality: int
    """

    picture = Image.open(file_path)
    picture.save(file_path, optimize=True, quality=quality)


def is_private_channel(ctx: ApplicationContext) -> bool:
    """
    Determines if a channel is a private conversation

    :param ctx: The context object
    :type ctx: ApplicationContext
    :return: True if private, False otherwise
    :rtype: bool
    """

    return ctx.channel.type.name == 'private'


async def check_permissions(ctx: ApplicationContext, bot: discord.Bot) -> bool:
    """
    Checks if a user has permissions to run commands

    :param ctx: The context object
    :type ctx: ApplicationContext
    :param bot: The bot object
    :type bot: discord.Bot
    :return: True if allowed, False otherwise
    :rtype: bool
    """

    if await bot.is_owner(ctx.author):
        return True
    if is_private_channel(ctx) and not database.check_private_permissions(ctx.author.id):
        await ctx.respond(text.PRIVATE_PERMISSIONS)
        return False
    if (not is_private_channel(ctx) and not database.check_guild_permissions(ctx.author.id, ctx.guild.id)
            and ctx.author != ctx.guild.owner):
        await ctx.respond(text.PERMISSIONS)
        return False
    return True
