from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod

D = TypeVar('D')
T = TypeVar('T')

stats_registry: list[StatGroup] = []

def register_stat_group(group: StatGroup):
    stats_registry.append(group)

class StatGroup(ABC, Generic[D]):
    """A group of statistics to be displayed together by the !stats command and how to get the relevant data from the db."""

    def __init__(self, name: str, display_label: str, items: list[StatItem] | None = None):
        self.name = name
        self.display_label = display_label
        self._items = items or []

    @abstractmethod
    async def fetch_data(self, dumbass_ids: list[int]) -> list[D]:
        ...

    @abstractmethod
    def group_by_user(self, data_entries: list[D]) -> dict[int, list[D]]:
        ...

    @property
    def items(self) -> list[StatItem[D, Any]]:
        return self._items.copy()

    def add_item(self, item: StatItem[D, Any]):
        self._items.append(item)
        item.parent_group = self
    
    def __iter__(self):
        return iter(self._items)

class StatItem(ABC, Generic[D, T]):
    """A single statistic to be displayed by the !stats command and how to calculate it."""
    
    def __init__(self, name: str, display_label: str, leaderboard_descending: bool = True):
        self.name = name
        self.display_label = display_label
        self.parent_group: StatGroup = None
        self.leaderboard_descending: bool = leaderboard_descending

    @abstractmethod
    def compute(self, data: list[D]) -> T:
        ...
    
    @abstractmethod
    def format(self, value: T) -> str:
        ...

def get_stat_item(stat_name: str) -> StatItem:
    for group in stats_registry:
        for item in group.items:
            if item.name == stat_name: return item
    return None