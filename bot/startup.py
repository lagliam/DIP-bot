# startup.py
# prepares and manages the restart process

import asyncio
import glob
import os
import bot.database as database

from bot.main_loop import main_loop
from bot.utility import log_event


async def startup(bot):
    log_event('Im restarting!')
    os.chdir("guilds")
    conn = database.sqlite_connection()
    create_startup_tables(conn)
    conn.close()
    for file in glob.glob("*.running"):
        file_parts = file.split('.')  # need the channel id
        if file_parts:
            channel = bot.get_channel(int(file_parts[1]))
            asyncio.create_task(main_loop(channel, file, file_parts[0], file_parts[1], restart=True))


def create_startup_tables(conn):
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS guilds(
       channel INT PRIMARY KEY,
       guild INT,
       post_amount INT,
       post_frequency INT,
       last_post REAL,
       all_seen TEXT);
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS images(
        guild INT,
        image TEXT);
    """)
    conn.commit()
