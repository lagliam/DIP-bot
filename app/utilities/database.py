# database.py
# Contains the database manipulation functions
import datetime
import os
import time

import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

from app.utilities import utility, constants


def database_connection() -> PooledMySQLConnection | MySQLConnectionAbstract:
    """
    Gets a connection to the database
    :return: The connection object
    :rtype: PooledMySQLConnection | MySQLConnectionAbstract
    """

    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'host': os.getenv('DB_HOST'),
        'database': 'db',
        'raise_on_warnings': True
    }
    return mysql.connector.connect(**config)


def get_channels() -> list:
    """
    Gets a list of channels from the database
    :return: The list of channels
    :rtype: list
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel FROM guilds')
    result = cur.fetchall()
    conn.close()
    return result


def get_active_channels() -> list[tuple]:
    """
    Gets only channels that haven't been marked as deleted
    :return: The list of channels
    :rtype: list
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT channel FROM guilds WHERE deleted = {False}')
    result = cur.fetchall()
    conn.close()
    return result


def start_posting_entry(channel_id: int, guild_id: int) -> None:
    """
    Creates a posting entry in the 'guilds' table

    :param channel_id: The channel id to post to
    :type channel_id: int
    :param guild_id: The guild id the channel resides in
    :type guild_id: int
    """

    defaults = (f'{channel_id}', f'{guild_id}', '1', '1', f'{time.time()}', False)
    conn = database_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO guilds VALUES(%s,%s,%s,%s,%s,%s);", defaults)
        conn.commit()
        conn.close()
    except Exception as error:
        conn.close()
        utility.log_event(f"Error while adding to db for guild {guild_id} {error}")


def write_viewed_image_list_for_guild(filename: str, guild_id: int) -> None:
    """
    Marks an image as viewed by creating a database entry

    :param filename: The file that was sent
    :type filename: str
    :param guild_id: The guild which received the image
    :type guild_id: int
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO images VALUES('{guild_id}', '{filename}', {False})")
    conn.commit()
    conn.close()


def get_seen_images(guild: int) -> list:
    """
    Gets a list of images that has already been posted unless they were marked as deleted

    :param guild: The guild that the images were posted to
    :type guild: int
    :return: A list of images that has been sent to the guild
    :rtype: list
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT image FROM images WHERE guild = {guild} AND deleted = {False}")
    result = cur.fetchall()
    conn.close()
    return result


def delete_seen_by_guild(guild_id: int) -> None:
    """
    Resets an image to unseen in the database by marking as deleted

    :param guild_id: The guild which receives the posts
    :type guild_id: int
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE images SET deleted = {True} WHERE guild = {guild_id}")
    conn.commit()
    conn.close()


def get_channel(channel_id: int) -> tuple:
    """
    Gets all columns from the 'guilds' table for a given channel

    :param channel_id: The channel to get
    :type channel_id: int
    :return: The fetched result
    :rtype: tuple
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM guilds WHERE channel = {channel_id}")
    result = cur.fetchone()
    conn.close()
    return result


def delete_channel(channel_id: int) -> None:
    """
    Marks a channel as deleted to stop posting to

    :param channel_id: The channel to stop posting to
    :type channel_id: int
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET deleted = {True} WHERE channel = {channel_id}")
    conn.commit()
    conn.close()


def get_database_entry(channel_id: int, key: str) -> tuple:
    """
    Gets a 'guilds' table entry

    :param channel_id: The channel whose data we want
    :type channel_id: int
    :param key: The column name to retrieve
    :type key: str
    :return: The retrieved data
    :rtype: tuple
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {key} FROM guilds WHERE channel = '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def set_database_entry(channel_id: int, key: str, value: any) -> None:
    """
    Sets an entry in the 'guilds' table

    :param channel_id: The channel to update
    :type channel_id: int
    :param key: The column name to update
    :type key: str
    :param value: The value to set the column to
    :type value: any
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET {key} = {value} WHERE channel = '{channel_id}'")
    conn.commit()
    conn.close()


def get_posting_amount(channel_id: int) -> int:
    """
    Gets the amount of posts for a channel

    :param channel_id: The channel to check number of posts
    :type channel_id: int
    :return: The number of posts the channel sends at a time
    :rtype: int
    """

    return get_database_entry(channel_id, 'post_amount')[0]


def get_posting_frequency(channel_id: int) -> int:
    """
    Gets the amount of posts per day to send

    :param channel_id: The channel being posted to
    :type channel_id: int
    :return: The posting frequency
    :rtype: int
    """

    return get_database_entry(channel_id, 'post_frequency')[0]


def get_last_post_date(channel_id: int) -> int:
    """
    Gets the time in seconds the last post was sent

    :param channel_id: The channel to check
    :type channel_id: int
    :return: The last post time in seconds
    :rtype: int
    """

    return get_database_entry(channel_id, 'last_post')[0]


def set_last_post_date(channel_id: int, date: float) -> None:
    """
    Sets the post time

    :param channel_id: The channel last posted to
    :type channel_id: int
    :param date: Time as represented by seconds
    :type date: float
    """

    set_database_entry(channel_id, 'last_post', date)


def set_post_amount(channel_id: int, amount: int) -> None:
    """
    Sets the amount of posts to send at a time

    :param channel_id: The channel to send to
    :type channel_id: int
    :param amount: The amount of posts to send
    :type amount: int
    """

    set_database_entry(channel_id, 'post_amount', amount)


def set_post_frequency(channel_id: int, amount: int) -> None:
    """
    Sets the number of posts per day

    :param channel_id: The channel to send to
    :type channel_id: int
    :param amount: The frequency of posts
    :type amount: int
    """

    set_database_entry(channel_id, 'post_frequency', amount)


def set_deleted_status(channel_id: int, status: bool) -> None:
    """
    Sets if a channel is deleted

    :param channel_id: The channel to stop posting to
    :type channel_id: int
    :param status: True to mark as deleted, False otherwise
    :type status: bool
    """

    set_database_entry(channel_id, 'deleted', status)


def is_image_seen(filename: str, guild_id: int) -> bool:
    """
    Gets if an image has been seen by the guild

    :param filename: The image file name
    :type filename: str
    :param guild_id: The guild that is posted to
    :type guild_id: int
    :return: True if seen, False otherwise
    :rtype: bool
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE image = '{filename}' AND guild = {guild_id} AND deleted = {False}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count > 0


def is_channel_deleted(channel_id: int) -> bool:
    """
    Determines if a channel has been deleted

    :param channel_id: The channel to check
    :type channel_id: int
    :return: True if marked as deleted, False otherwise
    :rtype: bool
    """

    deleted_status = get_database_entry(channel_id, 'deleted')
    if deleted_status is None:
        return True
    return bool(deleted_status[0])


def total_images_sent_to_guild(guild_id: int) -> int:
    """
    Gets the total number of posts that have been sent to the guild

    :param guild_id: The guild to check
    :type guild_id: int
    :return: Number of posts sent
    :rtype: int
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE guild = {guild_id}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count


def channels_posting_to_per_guild(guild_id: int) -> list:
    """
    The channel ids that are in a guild being posted to

    :param guild_id: The guild to check
    :type guild_id: int
    :return: The list of channel ids being posted to
    :rtype: list
    """

    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT channel FROM guilds WHERE guild = {guild_id}")
    channels = cur.fetchall()
    conn.close()
    return channels


def add_liked_image(parameters: dict) -> None:
    """
    Upserts a liked image to the database

    :param parameters: A dictionary containing the following parameters
        filename : str
        guild_id : int
        channel_id : int
    :type parameters: dict
    """

    conn = database_connection()
    cur = conn.cursor()
    now = datetime.datetime.now()
    find_sql = (f"SELECT id FROM liked_images "
                f"WHERE filename = '{parameters['filename']}' AND guild_id = {parameters['guild_id']} AND channel_id = {parameters['channel_id']}")
    cur.execute(find_sql)
    found_record_id = cur.fetchone()
    if found_record_id:
        update_sql = f"UPDATE liked_images SET counter = counter + 1, updated = '{now}' WHERE id = {found_record_id[0]}"
        cur.execute(update_sql)
    else:
        insert_sql = (f"INSERT INTO liked_images (filename, guild_id, channel_id, counter, updated) "
                      f"VALUES("
                      f"'{parameters['filename']}', "
                      f"{parameters['guild_id']}, "
                      f"{parameters['channel_id']}, "
                      f"1, "
                      f"'{now}'"
                      f")")
        cur.execute(insert_sql)
    conn.commit()
    conn.close()


def remove_liked_image(parameters: dict) -> None:
    """
    Decrements a liked image counter

    :param parameters: A dictionary containing the following parameters
        filename : str
        guild_id : int
        channel_id : int
    :type parameters: dict
    """
    conn = database_connection()
    cur = conn.cursor()
    now = datetime.datetime.now()
    find_sql = (f"SELECT id FROM liked_images "
                f"WHERE filename = '{parameters['filename']}' AND guild_id = {parameters['guild_id']} AND channel_id = {parameters['channel_id']}")
    cur.execute(find_sql)
    found_record_id = cur.fetchone()
    if found_record_id:
        update_sql = f"UPDATE liked_images SET counter = counter - 1, updated = '{now}' WHERE id = {found_record_id[0]}"
        cur.execute(update_sql)
        conn.commit()
    conn.close()


def get_top_liked_file(guild_id: int, channel_id: int) -> str:
    """
    Gets the most liked image for a guild and channel

    :param guild_id: The guild to check
    :type guild_id: int
    :param channel_id: The channel to check
    :type channel_id: int
    :return: The filename of the most liked image
    :rtype: str
    """
    conn = database_connection()
    cur = conn.cursor()
    sql_liked = f"SELECT filename, counter FROM liked_images WHERE guild_id = {guild_id} AND channel_id = {channel_id}"
    cur.execute(sql_liked)
    liked_images = cur.fetchall()
    conn.close()
    return sorted(liked_images, key=lambda x: x[1], reverse=True)[0][0]


def add_user(user_id: int, user_name: str, guild_id: int) -> None:
    """
    Upserts a user for executing bot commands

    :param user_id: The user id to allow
    :type user_id: int
    :param user_name: The display name of the user
    :type user_name: str
    :param guild_id: The guild to allow commands to run on
    :type guild_id: int
    """

    now = datetime.datetime.now()
    conn = database_connection()
    cur = conn.cursor()
    find_sql = (f"SELECT id FROM users "
                f"WHERE user_id = '{user_id}' AND guild_id = {guild_id}")
    cur.execute(find_sql)
    found_user = cur.fetchone()
    if not found_user:
        cur.execute(f"INSERT INTO users (user_id, user_name, guild_id, bot_permissions, updated, created) "
                    f"VALUES('{user_id}', '{user_name}', '{guild_id}', 2, '{now}', '{now}')")
        conn.commit()
    else:
        cur.execute(f"UPDATE users SET bot_permissions = 2, updated = '{now}' "
                    f"WHERE id = {found_user[0]}")
        conn.commit()
    conn.close()


def remove_user(user_id: int, guild_id: int) -> None:
    """
    Removes permissions from a user to disallow them from running commands

    :param user_id: The user id to disallow
    :type user_id: int
    :param guild_id: The guild where the commands should be prevented
    :type guild_id: int
    """

    now = datetime.datetime.now()
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET bot_permissions = 1, updated = '{now}' "
                f"WHERE user_id = {user_id} AND guild_id = {guild_id}")
    conn.commit()
    conn.close()


def check_guild_permissions(user_id: int, guild_id: int) -> bool:
    """
    Checks whether a user has permissions to execute commands in a guild

    :param user_id: The user id to check
    :type user_id: int
    :param guild_id: The guild to check
    :type guild_id: int
    :return: True if allowed, False otherwise
    :rtype: bool
    """

    find_sql = (f"SELECT bot_permissions FROM users "
                f"WHERE user_id = '{user_id}' AND guild_id = {guild_id}")
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(find_sql)
    found_record = cur.fetchone()
    conn.close()
    if not found_record:
        return False
    return found_record[0] >= 2


def check_private_permissions(user_id: int) -> bool:
    """
    Checks whether a user has permissions to interact with the bot in a private channel

    :param user_id: The id of the user
    :type user_id: int
    :return: True if allowed, False otherwise
    :rtype: bool
    """

    find_sql = (f"SELECT bot_permissions FROM users "
                f"WHERE user_id = '{user_id}' AND guild_id = NULL")
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(find_sql)
    found_record = cur.fetchone()
    conn.close()
    if not found_record:
        return False
    return found_record[0] == 3


def reset_last_viewed_for_channel(channel_id: int) -> None:
    """
    Resets the last viewed time for a channel

    :param channel_id: The channel to reset
    :type channel_id: int
    """

    last_post_date = datetime.datetime.fromtimestamp(float(get_last_post_date(channel_id)))
    posting_freq = int(get_posting_frequency(channel_id))
    next_post_timer = constants.TRIGGER_DURATION / posting_freq
    trigger_time = (last_post_date.timestamp() - next_post_timer) + constants.POLL_INTERVAL
    set_database_entry(channel_id, 'last_post', trigger_time)


def log_report(channel_id: int, guild_id: int | None, filename: str) -> None:
    """
    Stores a reported image in the database with a count of how many reports

    :param channel_id: The channel the post was sent to
    :type channel_id: int
    :param guild_id: The guild the post was sent to
    :type guild_id: int
    :param filename: The file name of the reported image
    :type filename: str
    """

    now = datetime.datetime.now()
    conn = database_connection()
    cur = conn.cursor()
    find_sql = (f"SELECT id FROM reported_images "
                f"WHERE channel_id = '{channel_id}' AND filename = '{filename}'")
    if guild_id is None:
        find_sql += ' AND guild_id IS NULL'
        guild = 'NULL'
    else:
        find_sql += f' AND guild_id = {guild_id}'
        guild = guild_id
    cur.execute(find_sql)
    found_report = cur.fetchone()
    if found_report:
        cur.execute(f"UPDATE reported_images SET counter = counter + 1, updated = '{now}' "
                    f"WHERE id = {found_report[0]}")
        conn.commit()
    else:
        cur.execute(f"INSERT INTO reported_images (channel_id, guild_id, filename, updated, created) "
                    f"VALUES('{channel_id}', {guild}, '{filename}', '{now}', '{now}')")
        conn.commit()
    conn.close()


def get_report_count(channel_id: int, guild_id: int | None, filename: str) -> int:
    """
    Gets a count of how many reports an image post has

    :param channel_id: The channel to check
    :type channel_id: int
    :param guild_id: The guild to check, None for private channel
    :type guild_id: int
    :param filename: The reported filename
    :type filename: str
    :return: The number of reports a file has had
    :rtype: int
    """
    conn = database_connection()
    cur = conn.cursor()
    find_sql = (f"SELECT counter FROM reported_images "
                f"WHERE channel_id = '{channel_id}' AND filename = '{filename}'")
    if guild_id is None:
        find_sql += ' AND guild_id IS NULL'
    else:
        find_sql += f' AND guild_id = {guild_id}'
    cur.execute(find_sql)
    found_report_count = cur.fetchone()[0]
    conn.close()
    return found_report_count
