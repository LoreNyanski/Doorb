from pypika import Query, Table, Order

import src.plugins.db as db
from src.pluginbot import setup_handler

class IncidentsTable():
    NAME = "incidents"
    INCIDENT_ID = "incident_id"
    DUMBASS_ID = "dumbass_id"
    OCCURANCE = "occurance"

INCIDENTS_TABLE = Table(IncidentsTable.NAME)

@setup_handler()
async def setup_incidents_table():
    """Ensures that there is an incidents table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {IncidentsTable.NAME} (
        {IncidentsTable.INCIDENT_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
        {IncidentsTable.DUMBASS_ID} INTEGER NOT NULL,
        {IncidentsTable.OCCURANCE} TEXT NOT NULL
        )
        """
    )

async def add_incident(dumbass_id: int, occurance: str):
    """Inserts an incident into the table named "incident" in the database"""
    q = Query.into(INCIDENTS_TABLE).columns(
        IncidentsTable.DUMBASS_ID, IncidentsTable.OCCURANCE
    ).insert(
        dumbass_id, occurance
    )   

    await db.execute_query(q.get_sql())

async def read_all_incidents(dumbass_ids: list[int]):
    """Returns the raw data of ALL incidents comitted by the dumbasses"""
    q = Query.from_(INCIDENTS_TABLE).select("*").where(
        INCIDENTS_TABLE[IncidentsTable.DUMBASS_ID].isin(dumbass_ids)
    )

    rows = await db.execute_query(q.get_sql())
    return rows if rows else []

async def read_last_guild_incident(dumbass_ids: list[int]):
    """Returns the last incident committed by ANYONE in dumbass_ids"""
    q = Query.from_(INCIDENTS_TABLE).select("*").where(
        INCIDENTS_TABLE[IncidentsTable.DUMBASS_ID].isin(dumbass_ids)
    ).orderby(INCIDENTS_TABLE[IncidentsTable.OCCURANCE], order=Order.desc).limit(1)

    rows = await db.execute_query(q.get_sql())
    return rows if rows else []