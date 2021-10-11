# utility.py
# contains the utility functions of the project

import os


def image_list(directory='../images/'):
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


def write_viewed_image_list_for_guild(filename, guild_id=None):
    with open(f'../guilds/images_{guild_id}.txt', 'a+') as f:
        f.write("%s\n" % filename)


def file_to_array(filename):
    array = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            array = f.readlines()
    return array


def delete_seen_by_guild(guild_id):
    with open(f'../guilds/images_{guild_id}.txt', 'r+') as file:
        file.truncate(0)
        file.close()


def get_posting_amount(guild_id, channel_id):
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    with open(running_file, 'r') as fp:
        for line in fp:
            key, value = line.split()
            if key == 'post_amount':
                return value


def get_posting_frequency(guild_id, channel_id):
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    with open(running_file, 'r') as fp:
        for line in fp:
            key, value = line.split()
            if key == 'post_frequency':
                return value


def wrap_by_word(s, n):
    '''returns a string where \\n is inserted between every n words'''
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i + n]) + '\n'

    return ret
