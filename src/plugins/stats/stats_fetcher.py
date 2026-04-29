from dataclasses import dataclass
from typing import Any
import logging

from .stats_strategy import StatItem, stats_registry

logger = logging.getLogger(__name__)

@dataclass
class StatResult:
    groups: list[StatGroupEntry]

@dataclass
class StatGroupEntry:
    name: str
    label: str
    items: list[StatItemEntry]

@dataclass
class StatItemEntry:
    name: str
    label: str
    value: Any
    formatted: str

@dataclass
class LeaderboardResult:
    name: str
    label: str
    entries: list[LeaderboardEntry]

@dataclass
class LeaderboardEntry:
    dumbass_id: int
    value: Any
    formatted: str

async def fetch_stats(dumbass_ids: list[int]) -> StatResult:
    groups = []
    for group in stats_registry:
        data_entries = await group.fetch_data(dumbass_ids)
        items = []
        for item in group.items:
            try:
                value = item.compute(data_entries)
                formatted = item.format(value)
            except Exception as e:
                value = None
                formatted = "iunno"
                logger.debug(f"Exception occured computing {item.name} value: {e}")
            items.append(StatItemEntry(name=item.name, label=item.display_label, value=value, formatted=formatted))
        groups.append(StatGroupEntry(name=group.name, label=group.display_label, items=items))
    return StatResult(groups=groups)


async def fetch_leaderboard(dumbass_ids: list[int], stat: StatItem) -> LeaderboardResult:
    entries: list[LeaderboardEntry] = []
    group = stat.parent_group
    data_entries = await group.fetch_data(dumbass_ids)
    entries_dict = group.group_by_user(data_entries)
    for dumbass_id in dumbass_ids:
        try:
            user_entries = entries_dict.get(dumbass_id, [])
            value = stat.compute(user_entries)
            formatted = stat.format(value)
        except Exception as e:
            value = None
            formatted = "iunno"
            logger.debug(f"Exception occured while computing {stat.name} value for {dumbass_id}: {e}")
        entries.append(LeaderboardEntry(dumbass_id=dumbass_id, value=value, formatted=formatted))
    entries.sort(
        key=lambda x: ((x.value is not None) if stat.leaderboard_descending else (x.value is None), x.value), 
        reverse=stat.leaderboard_descending)
    return LeaderboardResult(name=stat.name, label=stat.display_label, entries=entries)