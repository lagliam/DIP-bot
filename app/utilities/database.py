# database.py
# Contains the database manipulation functions
import datetime
import os
import time

import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

from app.utilities import utility, constants


def database_connection() ->  PooledMySQLConnection | MySQLConnectionAbstract:
    config = {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASS'),
        'host': os.getenv('DB_HOST'),
        'database': 'db',
        'raise_on_warnings': True
    }
    return mysql.connector.connect(**config)


def get_channels() -> list:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute('SELECT channel FROM guilds')
    result = cur.fetchall()
    conn.close()
    return result


def get_active_channels() -> list[tuple]:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f'SELECT channel FROM guilds WHERE deleted = {False}')
    result = cur.fetchall()
    conn.close()
    return result


def start_posting_entry(channel_id: int, guild_id: int) -> None:
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
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO images VALUES('{guild_id}', '{filename}', {False})")
    conn.commit()
    conn.close()


def get_seen_images(guild: int) -> list:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT image FROM images WHERE guild = {guild} AND deleted = {False}")
    result = cur.fetchall()
    conn.close()
    return result


def delete_seen_by_guild(guild_id: int) -> None:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE images SET deleted = {True} WHERE guild = {guild_id}")
    conn.commit()
    conn.close()


def get_channel(channel_id: int) -> tuple:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM guilds WHERE channel = {channel_id}")
    result = cur.fetchone()
    conn.close()
    return result


def delete_channel(channel_id: int) -> None:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET deleted = {True} WHERE channel = {channel_id}")
    conn.commit()
    conn.close()


def get_database_entry(channel_id: int, key: str) -> tuple:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {key} FROM guilds WHERE channel = '{channel_id}'")
    result = cur.fetchone()
    conn.close()
    return result


def set_database_entry(channel_id: int, key: str, value: any) -> None:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE guilds SET {key} = {value} WHERE channel = '{channel_id}'")
    conn.commit()
    conn.close()


def get_posting_amount(channel_id: int) -> int:
    return get_database_entry(channel_id, 'post_amount')[0]


def get_posting_frequency(channel_id: int) -> int:
    return get_database_entry(channel_id, 'post_frequency')[0]


def get_last_post_date(channel_id: int) -> int:
    return get_database_entry(channel_id, 'last_post')[0]


def set_last_post_date(channel_id: int, date: float) -> None:
    set_database_entry(channel_id, 'last_post', date)


def set_post_amount(channel_id: int, amount: int) -> None:
    set_database_entry(channel_id, 'post_amount', amount)


def set_post_frequency(channel_id: int, amount: int) -> None:
    set_database_entry(channel_id, 'post_frequency', amount)


def set_deleted_status(channel_id: int, status: bool) -> None:
    set_database_entry(channel_id, 'deleted', status)


def is_image_seen(filename: str, guild_id: int) -> bool:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE image = '{filename}' AND guild = {guild_id} AND deleted = {False}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count > 0


def is_channel_deleted(channel_id: int) -> bool:
    deleted_status = get_database_entry(channel_id, 'deleted')
    if deleted_status is None:
        return True
    return bool(deleted_status[0])


def total_images_sent_to_guild(guild_id: int) -> int:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM images WHERE guild = {guild_id}")
    seen_count = cur.fetchone()[0]
    conn.close()
    return seen_count


def channels_posting_to_per_guild(guild_id: int) -> list:
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT channel FROM guilds WHERE guild = {guild_id}")
    channels = cur.fetchall()
    conn.close()
    return channels


def add_liked_image(parameters: dict) -> None:
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


def get_top_liked_file(guild_id: int, channel_id: int) -> list:
    conn = database_connection()
    cur = conn.cursor()
    sql_liked = f"SELECT filename, counter FROM liked_images WHERE guild_id = {guild_id} AND channel_id = {channel_id}"
    cur.execute(sql_liked)
    liked_images = cur.fetchall()
    conn.close()
    return sorted(liked_images, key=lambda x: x[1], reverse=True)[0][0]


def add_user(user_id: int, user_name: str, guild_id: int) -> None:
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
    now = datetime.datetime.now()
    conn = database_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET bot_permissions = 1, updated = '{now}' "
                f"WHERE user_id = {user_id} AND guild_id = {guild_id}")
    conn.commit()
    conn.close()


def check_guild_permissions(user_id: int, guild_id: int) -> bool:
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
    last_post_date = datetime.datetime.fromtimestamp(float(get_last_post_date(channel_id)))
    posting_freq = int(get_posting_frequency(channel_id))
    next_post_timer = constants.TRIGGER_DURATION / posting_freq
    trigger_time = (last_post_date.timestamp() - next_post_timer) + constants.POLL_INTERVAL
    set_database_entry(channel_id, 'last_post', trigger_time)


def log_report(channel_id: int, guild_id: int | None, filename: str) -> None:
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


def get_report_count(channel_id: int, guild_id: int | None, filename: str):
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

