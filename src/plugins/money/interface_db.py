import src.plugins.db as db
from src.pluginbot import setup_handler

TABLE_ACCOUNTS = "accounts"
COL_DUMBASS_ID = "dumbass_id"
COL_BALANCE = "balance"
COL_LAST_DAILY = "last_daily"

TABLE_TRANSACTIONS = "transactions"
COL_TRANSACTION_ID = "transaction_id"
COL_SENDER_ID = "sender_id"
COL_RECIPIENT_ID = "recipient_id"
COL_AMOUNT = "amount"

@setup_handler()
async def setup_accounts_table(client):
    """Ensures that there is an accounts table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_ACCOUNTS} (
            {COL_DUMBASS_ID} INTEGER NOT NULL,
            {COL_BALANCE} INTEGER NOT NULL,
            {COL_LAST_DAILY} TEXT NOT NULL,
            PRIMARY KEY ({COL_DUMBASS_ID})
        );
        """
    )

@setup_handler()
async def setup_transactions_table(client):
    """Ensures that there is an transations table in the database if there wasn't one already"""
    await db.execute_query(
        f"""
        CREATE TABLE IF NOT EXISTS {TABLE_TRANSACTIONS} (
            {COL_TRANSACTION_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
            {COL_SENDER_ID} INTEGER NOT NULL,
            {COL_RECIPIENT_ID} INTEGER NOT NULL,
            {COL_AMOUNT} INTEGER NOT NULL
        );
        """
    )

async def read_account(dumbass_id: int):
    query = f"""
        SELECT {COL_DUMBASS_ID}, {COL_BALANCE}, {COL_LAST_DAILY}
        FROM {TABLE_ACCOUNTS}
        WHERE {COL_DUMBASS_ID} = ?
    """

    await db.execute_query(query, (dumbass_id))

async def write_transaction(sender_id: int, recipient_id: int, amount: int) -> str:
    query = f"""
        INSERT INTO {TABLE_TRANSACTIONS} ({COL_SENDER_ID}, {COL_RECIPIENT_ID}, {COL_AMOUNT}) 
        VALUES (?, ?, ?)
    """

    await db.execute_query(query, (sender_id, recipient_id, amount))
    
async def write_change_balance(dumbass_id: int, amount: int) -> str:
    query = f"""
        UPDATE {TABLE_ACCOUNTS}
        SET {COL_BALANCE} = {COL_BALANCE} + ?
        WHERE {COL_DUMBASS_ID} = ?
    """

    await db.execute_query(query, (amount, dumbass_id))

async def write_update_last_daily(dumbass_id: int, new_daily: str) -> str:
    query = f"""
        UPDATE {TABLE_ACCOUNTS}
        SET {COL_LAST_DAILY} = ?
        WHERE {COL_DUMBASS_ID} = ?
    """

    await db.execute_query(query, (new_daily, dumbass_id))
