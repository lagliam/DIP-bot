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


def get_running_file_entry(guild_id, channel_id, key):
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    with open(running_file, 'r') as fp:
        for line in fp:
            k, value = line.split()
            if k == key:
                return value


def get_posting_amount(guild_id, channel_id):
    return get_running_file_entry(guild_id, channel_id, 'post_amount')


def get_posting_frequency(guild_id, channel_id):
    return get_running_file_entry(guild_id, channel_id, 'post_frequency')


def get_last_post_date(guild_id, channel_id):
    return get_running_file_entry(guild_id, channel_id, 'last_post')


def get_all_seen_status(guild_id, channel_id):
    return get_running_file_entry(guild_id, channel_id, 'all_seen') == 'true'

def set_all_seen_status(guild_id, channel_id, status):
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    new_file = ""
    with open(running_file, 'r') as fp:
        for line in fp:
            key, _ = line.split()
            if key == 'all_seen':
                line = f'all_seen {status}\n'
            new_file += line
    write_file = open(f'../guilds/{guild_id}.{channel_id}.running', 'w')
    write_file.writelines(new_file)
    write_file.close()

def set_last_post_date(guild_id, channel_id, date):
    running_file = f'../guilds/{guild_id}.{channel_id}.running'
    new_file = ""
    with open(running_file, 'r') as fp:
        for line in fp:
            key, value = line.split()
            if key == 'last_post':
                line = f'last_post {date}\n'
            new_file += line
    write_file = open(f'../guilds/{guild_id}.{channel_id}.running', 'w')
    write_file.writelines(new_file)
    write_file.close()


def wrap_by_word(s, n):
    '''returns a string where \\n is inserted between every n words'''
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i + n]) + '\n'

    return ret
