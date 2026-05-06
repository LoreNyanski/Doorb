import sqlite3
import asyncio
from discord.ext.commands import Bot
from typing import Iterable

from src.pluginbot import setup_handler
from src.env import TEST_MODE

DB_PATH = "test.db" if TEST_MODE else "bot.db"

db_queue = asyncio.Queue()
worker = None
conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

conn.execute("PRAGMA journal_mode=WAL;")
conn.execute("PRAGMA busy_timeout=5000;")

async def db_worker():
    while True:
        query, params, future, many = await db_queue.get()
        try:
            cursor = conn.executemany(query, params) if many else conn.execute(query, params)
            conn.commit()
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                result = cursor.rowcount
            future.set_result(result)

        except Exception as e:
            future.set_exception(e)

        db_queue.task_done()

async def execute_query(query: str, params: Iterable=(), many: bool=False):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await db_queue.put((query, params, future, many))
    return await future

@setup_handler()
async def start_worker(bot: Bot):
    global worker
    worker = bot.loop.create_task(db_worker())