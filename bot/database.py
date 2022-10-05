import sqlite3
# https://towardsdatascience.com/python-sqlite-tutorial-the-ultimate-guide-fdcb8d7a4f30
from sqlite3 import Error


def sqlite_connection():
    try:
        con = sqlite3.connect('guilds.db')
        return con
    except Error:
        print(Error)
