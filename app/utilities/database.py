# database.py
# Contains the database manipulation functions

import sqlite3
import time
from pathlib import Path

from app.utilities import utility, constants


def sqlite_connection():
    db_path = constants.DB_PATH
    if Path(db_path).exists():
        try:
            con = sqlite3.connect(db_path)
            return con
        except sqlite3.Error:
            utility.log_event(sqlite3.Error)
    else:
        Path(db_path).touch()
        return sqlite_connection()


def create_startup_tables():
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS guilds(
       channel INT PRIMARY KEY,
       guild INT,
       post_amount INT,
       post_frequency INT,
       last_post REAL,
       all_seen INT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS images(
        guild INT,
        image TEXT);
    """)
    conn.commit()


def get_channels():
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel FROM guilds')
    result = cur.fetchall()
    conn.close()
    return result


def start_posting_entry(channel_id, guild_id):
    defaults = (f'{channel_id}', f'{guild_id}', '1', '1', f'{time.time()}', '0')
    conn = sqlite_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO guilds VALUES(?,?,?,?,?,?);", defaults)
        conn.commit()
        conn.close()
    except sqlite3.Error as error:
        conn.close()
        utility.log_event(f"Error while adding to db for guild {guild_id} {error}")


def write_viewed_image_list_for_guild(filename, guild_id):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO images VALUES('{guild_id}', '{filename}')")
    conn.commit()
    conn.close()


def get_seen_images(guild):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT image FROM images WHERE guild is {guild}")
    result = cur.fetchall()
    conn.close()
    return result


def delete_seen_by_guild(guild_id):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM images WHERE guild is {guild_id}")
    conn.commit()
    conn.close()


def get_channel(channel_id):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM guilds WHERE channel is '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def delete_channel(channel_id):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM guilds WHERE channel is {channel_id}")
    conn.commit()
    conn.close()


def get_database_entry(channel_id, key):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {key} FROM guilds WHERE channel is '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def set_database_entry(channel_id, key, value):
    conn = sqlite_connection()
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


def is_image_seen(filename, guild_id):
    conn = sqlite_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE image is '{filename}' AND guild is {guild_id}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count > 0
