import discord
import os
import psycopg2
import logging
from config import dbConfig, useDB

# $ createdb lynnDB

if useDB:
    conn = psycopg2.connect(database=dbConfig['database'],
                            user=dbConfig['user'],
                            password=dbConfig['password'],
                            host=dbConfig['host'],
                            port=dbConfig['port'])
    conn.set_session(autocommit=True)
    
    cur = conn.cursor()
    
    cur.execute('''CREATE TABLE IF NOT EXISTS guilds
                (id BIGINT PRIMARY KEY      NOT NULL,
                disabledmodules TEXT,
                prefix          TEXT,
                customcommands  TEXT);''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS users
                (id BIGINT PRIMARY KEY      NOT NULL,
                location   TEXT);''')

async def setUser(id, key, value):
    cur.execute('SELECT * FROM users WHERE id = %s', (id,))
    res = cur.fetchone()
    if not res:
        cur.execute('''INSERT INTO users (id, location)
                    VALUES (%s, '')''', (id,))
        cur.execute('SELECT * FROM users WHERE id = %s', (id,))
        res = cur.fetchone()

    # 'UPDATE users SET %s = %s WHERE id = %s' doesn't work since %s includes quotes
    cur.execute('UPDATE users SET {} = %s WHERE id = %s'.format(key), (value, id))

async def setGuild(id, key, value):
    cur.execute('SELECT * FROM guilds WHERE id = %s', (id,))
    res = cur.fetchone()
    if not res:
        cur.execute('''INSERT INTO guilds (id, disabledmodules, prefix, customcommands)
                    VALUES (%s, '', '', '')''', (id,))
        cur.execute('SELECT * FROM guilds WHERE id = %s', (id,))
        res = cur.fetchone()

    cur.execute('UPDATE guilds SET {} = %s WHERE id = %s'.format(key), (value, id))

async def getValue(table, id, key):
    # There's probably some workaround for this, but for now this could cause sql injection issues
    # if called with untrusted data
    cur.execute(f'SELECT {key} FROM {table} WHERE id = {id}')
    res = cur.fetchone()
    if not res:
        return None
    return res[0]