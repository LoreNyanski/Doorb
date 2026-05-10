from dataclasses import dataclass

from src.plugins.stats import StatContext, StatGroup, StatItem, register_stat_group
from src.pluginbot import sig_setup

from .money_schema import Account


sig_setup.connect
async def setup_money_stats(client):
    group = MoneyStatGroup("money_stats", "Money")
    
    group.add_item(StatBalance("balance", "Balance"))

@dataclass
class MoneyStatContext(StatContext):
    accounts: list[Account]

class MoneyStatGroup(StatGroup):

    async def fetch_data(self, dumbass_ids) -> list[Account]:
        return [Account.get_account(dumbass_id) for dumbass_id in dumbass_ids]
    
    def group_by_user(self, entries: list[Account]) -> dict[int, Account]:
        return {account.dumbass_id : account for account in entries}
    
    def build_context(self, entries):
        return MoneyStatContext(entries)

class StatBalance(StatItem):

    def compute(self, context: MoneyStatContext):
        return sum([account.balance for account in context.accounts])
    
    def format(self, value):
        return f"{value}"