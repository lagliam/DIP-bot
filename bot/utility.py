# utility.py
# contains the utility functions of the project

import logging
import os
import sys

import bot.database


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


def write_viewed_image_list_for_guild(filename, guild_id):
    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO images VALUES('{guild_id}', '{filename}')")
    conn.commit()
    conn.close()


def get_seen_images(guild):
    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT image FROM images WHERE guild is {guild}")
    result = cur.fetchall()
    conn.close()
    return result


def delete_seen_by_guild(guild_id):
    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM images WHERE guild is {guild_id}")
    conn.commit()
    conn.close()


def get_database_entry(channel_id, key):
    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {key} FROM guilds WHERE channel is '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def set_database_entry(channel_id, key, value):
    conn = bot.database.sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET {key} = {value} WHERE channel = '{channel_id}'")
    conn.commit()
    conn.close()


def get_posting_amount(channel_id):
    return get_database_entry(channel_id, 'post_amount')[0]


def get_posting_frequency(channel_id):
    return get_database_entry(channel_id, 'post_frequency')[0]


def get_last_post_date(channel_id):
    return get_database_entry(channel_id, 'last_post')[0]


def get_all_seen_status(channel_id):
    return get_database_entry(channel_id, 'all_seen')[0] == '1'


def set_all_seen_status(channel_id, status):
    set_database_entry(channel_id, 'all_seen', status)


def set_last_post_date(channel_id, date):
    set_database_entry(channel_id, 'last_post', date)


def set_post_amount(channel_id, amount):
    set_database_entry(channel_id, 'post_amount', amount)


def set_post_frequency(channel_id, amount):
    set_database_entry(channel_id, 'post_frequency', amount)


def wrap_by_word(s, n):
    """returns a string where \\n is inserted between every n words"""
    a = s.split()
    ret = ''
    for i in range(0, len(a), n):
        ret += ' '.join(a[i:i + n]) + '\n'

    return ret


def log_event(message):
    logging.basicConfig(stream=sys.stdout, format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info(message)
