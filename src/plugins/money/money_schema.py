from datetime import datetime

from src.utils import utc_to_ams

from .interface_db import write_account, read_account

DEFAULT_BALANCE = 500
DEFAULT_LAST_DAILY = datetime.min

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

    def balance_check(self, required_amount: int) -> bool:
        return (required_amount < self.balance) and (required_amount >= 0)
        
    def daily_check(self, current_time: datetime) -> bool:
        return utc_to_ams(self.last_daily) < utc_to_ams(current_time).date()

    def add_balance(self, amount: int):
        self.balance += amount

    def create_transation(self, recipient: Account, amount: int) -> Transaction:
        return Transaction(self, recipient, amount)
        
    
    

class Transaction:
    
    def __init__(self, sender: Account, receiver: Account, amount: int):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def payout():
        pass