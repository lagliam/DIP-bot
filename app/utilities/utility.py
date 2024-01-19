# utility.py
# contains the utility functions of the project

import logging
import os
import random

from app.utilities import constants


def get_cogs():
    directory_contents = os.listdir('app/cogs')
    cogs = []
    for content in directory_contents:
        if os.path.isfile('app/cogs/' + content):
            cogs.append(content.split('.')[0])
    return cogs


def image_list(directory):
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


def log_event(message):
    logging.basicConfig(
        handlers=[logging.FileHandler('log/dip-bot.log'), logging.StreamHandler()],
        format='%(asctime)s - %(message)s',
        level=logging.INFO
    )
    logging.info(message)


def get_file(file_list):
    filename = file_list.pop(random.randrange(len(file_list)))
    while is_large_file(constants.IMAGES_PATH + filename):
        log_event(f'Image {filename} too large to send')
        try:
            filename = file_list.pop(random.randrange(len(file_list)))
        except ValueError:
            log_event('All files are too big to send')
            filename = None
            break
    return filename


def is_large_file(filepath):
    return os.path.getsize(filepath) > constants.LIMIT_SIZE
