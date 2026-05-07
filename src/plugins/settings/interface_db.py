from typing import Any

import src.plugins.db as db
from src.pluginbot import sig_setup

TABLE_GUILD_SETTINGS = "guild_settings"
TABLE_DUMBASS_SETTINGS = "dumbass_settings"
COL_GUILD_ID = "guild_id"
COL_DUMBASS_ID = "dumbass_id"
COL_KEY = "key"
COL_VALUE = "value"

@sig_setup.connect
async def setup_guild_settings_table(client):
    """Ensures that there is an incidents table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_GUILD_SETTINGS} (
            {COL_GUILD_ID} INTEGER NOT NULL,
            {COL_KEY} TEXT NOT NULL,
            {COL_VALUE} TEXT NOT NULL,
            PRIMARY KEY ({COL_GUILD_ID}, {COL_KEY})
        );
        """
    )

@sig_setup.connect
async def setup_dumbass_settings_table(client):
    """Ensures that there is an incidents table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_DUMBASS_SETTINGS} (
            {COL_DUMBASS_ID} INTEGER NOT NULL,
            {COL_KEY} TEXT NOT NULL,
            {COL_VALUE} TEXT NOT NULL,
            PRIMARY KEY ({COL_DUMBASS_ID}, {COL_KEY})
        );
        """
    )


async def read_guild_settings(guild_id: int, keys: list[str]):
    if not keys:
        return []

    placeholders = ",".join("?" for _ in keys)

    query = f"""
        SELECT {COL_KEY}, {COL_VALUE}
        FROM {TABLE_GUILD_SETTINGS}
        WHERE {COL_GUILD_ID} = ?
        AND {COL_KEY} IN ({placeholders})
    """

    params = (guild_id, *keys)
    return await db.execute_query(query, params) or []

async def read_dumbass_settings(dumbass_id: int, keys: list[str]):
    if not keys:
        return []

    placeholders = ",".join("?" for _ in keys)

    query = f"""
        SELECT {COL_KEY}, {COL_VALUE}
        FROM {TABLE_DUMBASS_SETTINGS}
        WHERE {COL_DUMBASS_ID} = ?
        AND {COL_KEY} IN ({placeholders})
    """

    params = (dumbass_id, *keys)
    return await db.execute_query(query, params) or []

async def write_guild_settings(guild_id: int, values: dict[str, str]):
    if not values:
        return

    query = f"""
        INSERT INTO {TABLE_GUILD_SETTINGS} ({COL_GUILD_ID}, {COL_KEY}, {COL_VALUE})
        VALUES (?, ?, ?)
        ON CONFLICT({COL_GUILD_ID}, {COL_KEY})
        DO UPDATE SET {COL_VALUE} = excluded.{COL_VALUE}
    """

    params = [(guild_id, key, value) for key, value in values.items()]
    await db.execute_query(query, params, many=True)

async def write_dumbass_settings(dumbass_id: int, values: dict[str, str]):
    if not values:
        return

    query = f"""
        INSERT INTO {TABLE_DUMBASS_SETTINGS} ({COL_DUMBASS_ID}, {COL_KEY}, {COL_VALUE})
        VALUES (?, ?, ?)
        ON CONFLICT({COL_DUMBASS_ID}, {COL_KEY})
        DO UPDATE SET {COL_VALUE} = excluded.{COL_VALUE}
    """

    params = [(dumbass_id, key, value) for key, value in values.items()]
    await db.execute_query(query, params, many=True)