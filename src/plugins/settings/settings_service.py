from typing import Any
from enum import Enum

from .settings_schema import settings_registry
from .interface_db import read_guild_settings, read_dumbass_settings, write_dumbass_settings, write_guild_settings

class Scope(Enum):
    GUILD = 0
    DUMBASS = 1

_settings_cache: dict[tuple[Scope, int, str], Any] = {}

async def get_settings(scope: Scope, subject_id: int, keys: list[str]) -> dict[str, Any]:
    """Get multiple settings at once. The return value is a dictionary of {setting_key:value}"""
    result: dict[str, Any] = {}
    reader = read_guild_settings if scope == Scope.GUILD else read_dumbass_settings 
    # this is fine for now. if it needs to be extended later use a dict or something.
    
    # Get all cached values
    noncached_keys = []
    base = (scope, subject_id)
    for key in keys:
        cache_key = (*base, key)
        if cache_key in _settings_cache:
            result[key] = _settings_cache[cache_key]
        else:
            noncached_keys.append(key)

    # Get all stored values
    missing_keys = set(noncached_keys)
    if noncached_keys:
        rows = await reader(subject_id, noncached_keys)
        for key, str_value in rows: # [(key, value), (key, value)...]
            setting = settings_registry[key]
            value = setting.parser(str_value)
            result[key] = value
            _settings_cache[(scope, subject_id, key)] = value
            missing_keys.discard(key)
    
    # Fill the rest with defaults
    for key in missing_keys:
        setting = settings_registry[key]
        result[key] = setting.default
        _settings_cache[(scope, subject_id, key)] = setting.default

    return result

async def get_setting(scope: Scope, subject_id: int, key: str):
    """Get a single setting (wraps get_settings)"""
    result = await get_settings(scope, subject_id, [key])
    return result[key]

async def set_settings(scope: Scope, subject_id: int, values: dict[str, Any]):
    """Set multiple settings at once."""
    if not values: return
    setter = write_guild_settings if scope == Scope.GUILD else write_dumbass_settings 
    # this is fine for now. if it needs to be extended later use a dict or something.

    serialized: dict[str, str] = {}
    for key, value in values.items():
        setting = settings_registry[key]
        serialized[key] = setting.serializer(value)

    await setter(subject_id, serialized) 

async def set_setting(scope: Scope, subject_id: int, key: str, value: Any):
    """Set a single setting (wraps set_settings)"""
    await set_settings(scope, subject_id, {key : value})