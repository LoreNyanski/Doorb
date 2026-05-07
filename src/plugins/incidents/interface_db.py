import src.plugins.db as db
from src.pluginbot import sig_setup

TABLE_INCIDENTS = "incidents"

COL_INCIDENT_ID = "incident_id"
COL_DUMBASS_ID = "dumbass_id"
COL_OCCURRENCE = "occurrence"

@sig_setup.connect
async def setup_incidents_table(client):
    """Ensures that there is an incidents table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_INCIDENTS} (
        {COL_INCIDENT_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {COL_DUMBASS_ID} INTEGER NOT NULL,
        {COL_OCCURRENCE} TEXT NOT NULL
        )
        """
    )

async def add_incident(dumbass_id: int, occurrence: str):
    """Inserts an incident into the table named "incident" in the database"""
    await db.execute_query(
        f"INSERT INTO {TABLE_INCIDENTS} ({COL_DUMBASS_ID}, {COL_OCCURRENCE}) VALUES (?, ?)",
        (dumbass_id, occurrence)
    )

async def read_all_incidents(dumbass_ids: list[int]):
    """Returns the raw data of ALL incidents comitted by the dumbasses"""
    if not dumbass_ids:
        return []

    placeholders = ",".join("?" for _ in dumbass_ids)

    query = f"""
        SELECT {COL_INCIDENT_ID}, {COL_DUMBASS_ID}, {COL_OCCURRENCE}
        FROM {TABLE_INCIDENTS}
        WHERE {COL_DUMBASS_ID} IN ({placeholders})
    """

    return await db.execute_query(query, tuple(dumbass_ids)) or []

async def read_last_guild_incident(dumbass_ids: list[int]):
    """Returns the last incident committed by ANYONE in dumbass_ids"""
    if not dumbass_ids:
        return []

    placeholders = ",".join("?" for _ in dumbass_ids)

    query = f"""
        SELECT {COL_INCIDENT_ID}, {COL_DUMBASS_ID}, {COL_OCCURRENCE}
        FROM {TABLE_INCIDENTS}
        WHERE {COL_DUMBASS_ID} IN ({placeholders})
        ORDER BY {COL_OCCURRENCE} DESC
        LIMIT 1
    """

    return await db.execute_query(query, tuple(dumbass_ids)) or []