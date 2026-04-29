from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

def utc_to_ams(utc_time: datetime):
    """returns the input utc time as ams localised time"""
    return utc_time.astimezone(ZoneInfo("Europe/Amsterdam"))

def format_timedelta(time: timedelta) -> str:
    """outputs a timedelta in the format "  1d  2h  3m  4s"""
    days = time.days
    hours = time.seconds // 3600
    minutes = time.seconds % 3600 // 60
    seconds = time.seconds % 3600 % 60

    parts = []

    if days:
        parts.append(f"{days:>3}d")
    if hours or days:
        parts.append(f"{hours:>2}h")
    if minutes or hours or days:
        parts.append(f"{minutes:>2}m")

    parts.append(f"{seconds:>2}s")
    return " ".join(parts)