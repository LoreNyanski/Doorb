from pypika import Table, Query
from typing import Any

import src.plugins.db as db

GUILD_TABLE = Table("guild_settings")
DUMBASS_TABLE = Table("dumbass_settings")

async def read_guild_settings(guild_id: int, keys: list[str]):
    query = Query.from_(GUILD_TABLE).select(GUILD_TABLE.key, GUILD_TABLE.value).where(
        (GUILD_TABLE.guild_id == guild_id) & GUILD_TABLE.key.isin(keys)
    )
    rows = await db.execute_query(query)
    return rows

async def read_dumbass_settings(dumbass_id: int, keys: list[str]):
    query = Query.from_(DUMBASS_TABLE).select(DUMBASS_TABLE.key, DUMBASS_TABLE.value).where(
        (DUMBASS_TABLE.dumbass_id == dumbass_id) & DUMBASS_TABLE.key.isin(keys)
    )
    rows = await db.execute_query(query)
    return rows

async def write_guild_settings(guild_id: int, values: dict[str, Any]):
    query = f"""
    INSERT INTO guild_settings (guild_id, key, value)
    VALUES (?, ?, ?)
    ON CONFLICT(guild_id, key)
    DO UPDATE SET value=excluded.value
    """

    params = [(guild_id, key, value) for key, value in values.items()]
    db.execute_query(query, params, many=True)

async def write_dumbass_settings(dumbass_id: int, values: dict[str, Any]):
    query = f"""
    INSERT INTO dumbass_settings (dumbass_id, key, value)
    VALUES (?, ?, ?)
    ON CONFLICT(dumbass_id, key)
    DO UPDATE SET value=excluded.value
    """

    params = [(dumbass_id, key, value) for key, value in values.items()]
    db.execute_query(query, params, many=True)