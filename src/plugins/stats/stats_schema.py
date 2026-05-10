from typing import TypeVar, Generic, Any
from abc import ABC, abstractmethod

stats_registry: list[StatGroup] = []

def register_stat_group(group: StatGroup):
    stats_registry.append(group)

class StatContext:
    """Derived, computation-ready view over a list of entries."""
    ...

T_Entry = TypeVar('E')
T_Context = TypeVar('C', bound=StatContext)
T_Value = TypeVar('V')

class StatGroup(ABC, Generic[T_Entry, T_Context]):
    """A group of statistics to be displayed together by the !stats command and how to get the relevant data from the db."""

    def __init__(self, name: str, display_label: str):
        self.name = name
        self.display_label = display_label
        self.items: list[StatItem] = []
        register_stat_group(self)

    @abstractmethod
    async def fetch_data(self, dumbass_ids: list[int]) -> list[T_Entry]:
        """Fetches all relevant db entries and returns them parsed"""
        ...

    @abstractmethod
    def group_by_user(self, entries: list[T_Entry]) -> dict[int, list[T_Entry]]:
        "Partitions all entries per user"
        ...

    @abstractmethod
    def build_context(self, entries: list[T_Entry]) -> T_Context:
        "Converts a partition of entries into a computation context for StatItems"
        ...

    def add_item(self, item: StatItem[T_Context, Any]):
        self.items.append(item)
        item.parent_group = self
    
    def __iter__(self):
        return iter(self.items)

class StatItem(ABC, Generic[T_Context, T_Value]):
    """A single statistic to be displayed by the !stats command and how to calculate it."""
    
    def __init__(self, name: str, display_label: str, leaderboard_descending: bool = True):
        self.name = name
        self.display_label = display_label
        self.parent_group: StatGroup = None
        self.leaderboard_descending: bool = leaderboard_descending

    @abstractmethod
    def compute(self, context: T_Context) -> T_Value:
        """Computes a value out of the context object"""
        ...
    
    @abstractmethod
    def format(self, value: T_Value) -> str:
        """Turns the value into a displayable string"""
        ...

def get_stat_item(stat_name: str) -> StatItem:
    for group in stats_registry:
        for item in group.items:
            if item.name == stat_name: return item
    return None