from datetime import datetime, timedelta
from dataclasses import dataclass
import random as r


from src.utils import utc_to_ams

from .interface_db import write_account, read_account, write_transaction

DEFAULT_BALANCE = 500
DEFAULT_LAST_DAILY = datetime.min

BANK_ID = 0

_account_cache: dict[int, Account] = {}

class Account:
    
    def __init__(self, dumbass_id: int, balance: int = DEFAULT_BALANCE, last_daily: datetime = DEFAULT_LAST_DAILY):
        self.dumbass_id = dumbass_id
        self.balance = balance
        self.last_daily = last_daily

    @staticmethod
    def _parser(row: tuple[int, int, str]) -> Account:
        dumbass_id, balance, last_daily = row
        parsed_last_daily = datetime.fromisoformat(last_daily)
        return Account(dumbass_id, balance, parsed_last_daily)

    @staticmethod
    async def get_account(dumbass_id: int) -> Account:
        if dumbass_id in _account_cache:
            account = _account_cache[dumbass_id]
        else:
            rows = await read_account(dumbass_id)
            account = Account._parser(rows[0]) if rows else Account(dumbass_id)
            _account_cache[dumbass_id] = account
        return account
    
    def _serializer(self) -> tuple[int, int, str]:
        serialized_last_daily = self.last_daily.isoformat()
        return (self.dumbass_id, self.balance, serialized_last_daily)

    async def save(self):
        row = self._serializer()
        await write_account(row)
        
    def can_claim_daily(self, current_time: datetime) -> bool:
        return utc_to_ams(self.last_daily) < utc_to_ams(current_time).date()

    def can_withdraw(self, amount: int) -> bool:
        return amount <= self.balance

    def withdraw(self, amount: int):
        if amount < 0:
            raise ValueError("Withdrawal can't be negative")
        if not self.can_withdraw(amount):
            raise ValueError("Insufficient funds")
        self.balance -= amount

    def deposit(self, amount: int):
        if amount < 0:
            raise ValueError("Deposit can't be negative")
        self.balance += amount
        
@dataclass
class Transaction:
    sender_id: int
    receiver_id: int
    amount: int
    timestamp: datetime

    def _serializer(self) -> tuple[int, int, int, str]:
        serialized_timestamp = self.timestamp.isoformat()
        return (self.sender_id, self.receiver_id, self.amount, serialized_timestamp)

    async def save(self):
        row = self._serializer()
        await write_transaction(row)        

async def transfer(sender: Account, receiver: Account, amount: int, now: datetime):
    transaction = Transaction(sender.dumbass_id, receiver.dumbass_id, amount, now)
    await transaction.save()

    sender.withdraw(amount)
    receiver.deposit(amount)
    await sender.save()
    await receiver.save()

async def grant_money(receiver: Account, amount: int, now: datetime):
    transaction = Transaction(BANK_ID, receiver.dumbass_id, amount, now)
    await transaction.save()

    receiver.deposit(amount)
    await receiver.save()





async def do_daily(account: Account, now: datetime) -> tuple[bool, int]:
    roll = r.randint(1, 1000)
    success = False

    if account.can_claim_daily(now):
        success = True
        account.last_daily = now
        # await account.save() 
        await grant_money(account, roll, now)
    
    return (success, roll)

def time_until_midnight(now: datetime) -> timedelta:
    return utc_to_ams(now).time()