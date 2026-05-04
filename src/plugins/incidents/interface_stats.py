from datetime import timedelta, time, timezone, datetime
from statistics import mean, median
from collections import defaultdict
from dataclasses import dataclass

from src.utils import format_timedelta, utc_to_ams
from src.pluginbot import setup_handler
from src.plugins.stats import StatGroup, StatItem, StatContext, register_stat_group

from .interface_db import read_all_incidents
from .incident_schema import Incident, IncidentInterval

@setup_handler()
async def setup_incident_stat_group(client):
    group = IncidentGroup("incident_stats", "Incidents")
    
    group.add_item(StatCount("count", "Total incidents"))
    group.add_item(StatMean("mean", "Avg time between", False))
    group.add_item(StatMedian("median", "Med time between", False))
    group.add_item(StatMax("max", "Longest streak"))
    group.add_item(StatMin("min", "Shortest streak", False))
    group.add_item(StatBusiestDay("busiest_day", "Most in 24 hours"))
    group.add_item(StatPrimeHour("prime_hour", "Unluckiest hour"))
    group.add_item(StatLast("last", "Current streak"))

    register_stat_group(group)



@dataclass
class IncidentStatContext(StatContext):
    """A sorted list of incidents and the intervals between them"""
    incidents: list[Incident]
    intervals: list[IncidentInterval]

class IncidentGroup(StatGroup[Incident, IncidentStatContext]):
    def __init__(self, name, display_label):
        super().__init__(name, display_label)

    async def fetch_data(self, dumbass_ids):
        rows = await read_all_incidents(dumbass_ids)
        incidents = [Incident.parser(row) for row in rows]
        return incidents

    def group_by_user(self, entries):
        result = defaultdict(list)
        for e in entries:
            result[e.dumbass_id].append(e)
        return result
    
    def build_context(self, entries):
        sorted_entries = sorted(entries, key=lambda x: x.occurrence)
        return IncidentStatContext(
            incidents=sorted_entries,
            intervals= [sorted_entries[i] - sorted_entries[i-1] for i in range(1, len(sorted_entries))]
        )

class StatCount(StatItem[IncidentStatContext, int]):
    """Returns the amount of incidents"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        return len(context.incidents)
    
    def format(self, value):
        return f"{value} "

class StatMean(StatItem[IncidentStatContext, timedelta]):
    """Returns the mean length between the incidents."""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        return mean([interval.length for interval in context.intervals])

    def format(self, value):
        return format_timedelta(value)

class StatMedian(StatItem[IncidentStatContext, timedelta]):
    """Returns the median length between the incidents"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        return median([interval.length for interval in context.intervals])
    
    def format(self, value):
        return format_timedelta(value)
    
class StatMax(StatItem[IncidentStatContext, timedelta]):
    """Returns the max length between the incidents"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        return max(context.intervals).length
    
    def format(self, value):
        return format_timedelta(value)

class StatMin(StatItem[IncidentStatContext, timedelta]):
    """Returns the min length between the incidents"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        return min(context.intervals).length
    
    def format(self, value):
        return format_timedelta(value)
    
class StatLast(StatItem[IncidentStatContext, timedelta]):
    """Retruns the length since the last incidents"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)
    
    def compute(self, context):
        return datetime.now(tz=timezone.utc) - context.incidents[-1].occurrence
    
    def format(self, value):
        return format_timedelta(value)

class StatBusiestDay(StatItem[IncidentStatContext, int]):
    """Returns the largest number of incidents in 24 hours"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        if len(context.incidents) == 0: return 0
        # okay so this algo is technically correct, however, the window isn't always a correct 24h window which is cursed but funni
        window: list[Incident] = [context.incidents[0]]
        for incident in context.incidents[1:]: 
            window.append(incident)
            delta = incident.occurrence - window[0].occurrence
            if delta > timedelta(days=1): window.remove(window[0])
        return len(window)
    
    def format(self, value):
        return f"{value} "

class StatPrimeHour(StatItem[IncidentStatContext, time]):
    """Returns the hour of day where the most incidents happened"""

    def __init__(self, name, display_label, leaderboard_descending = True):
        super().__init__(name, display_label, leaderboard_descending)

    def compute(self, context):
        if len(context.incidents) == 0: return time()
        buckets = [0] * 24
        for inc in context.incidents:
            i = utc_to_ams(inc.occurrence).hour
            buckets[i] += 1
        prime_hour = max(range(24), key=lambda x: buckets[x])
        return time(hour=prime_hour)
    
    def format(self, value):
        return str(value)
