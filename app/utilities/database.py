# database.py
# Contains the database manipulation functions
import os
import time

import mysql.connector

from app.utilities import utility


def database_connection():
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'host': os.getenv('DB_HOST'),
        'database': 'db',
        'raise_on_warnings': True
    }
    return mysql.connector.connect(**config)


def get_channels():
    conn = database_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel FROM guilds')
    result = cur.fetchall()
    conn.close()
    return result


def get_active_channels():
    conn = database_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel FROM guilds WHERE deleted = 0')
    result = cur.fetchall()
    conn.close()
    return result


def start_posting_entry(channel_id, guild_id):
    defaults = (f'{channel_id}', f'{guild_id}', '1', '1', f'{time.time()}', '0')
    conn = database_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO guilds VALUES(%s,%s,%s,%s,%s,%s);", defaults)
        conn.commit()
        conn.close()
    except Exception as error:
        conn.close()
        utility.log_event(f"Error while adding to db for guild {guild_id} {error}")


def write_viewed_image_list_for_guild(filename, guild_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO images VALUES('{guild_id}', '{filename}')")
    conn.commit()
    conn.close()


def get_seen_images(guild):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT image FROM images WHERE guild = {guild}")
    result = cur.fetchall()
    conn.close()
    return result


def delete_seen_by_guild(guild_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM images WHERE guild = {guild_id}")
    conn.commit()
    conn.close()


def get_channel(channel_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM guilds WHERE channel = {channel_id}")
    result = cur.fetchone()
    conn.close()
    return result


def delete_channel(channel_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET deleted = {True} WHERE channel = {channel_id}")
    conn.commit()
    conn.close()


def get_database_entry(channel_id, key):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {key} FROM guilds WHERE channel = '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def set_database_entry(channel_id, key, value):
    conn = database_connection()
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


def set_deleted_status(channel_id, status: bool):
    set_database_entry(channel_id, 'deleted', status)


def is_image_seen(filename, guild_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE image = '{filename}' AND guild = {guild_id}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count > 0


def is_channel_deleted(channel_id):
    deleted_status = get_database_entry(channel_id, 'deleted')
    if deleted_status is None:
        return True
    return bool(deleted_status[0])
