import logging
import inspect
import os
import importlib
from discord.ext.commands import Bot

import src.plugins

logger = logging.getLogger(__name__)

plugins_path = src.plugins.__path__[0]

setups = []

class PluginBot(Bot):
    """A discord bot that executes all functions registered with the @on_startup() decorator before it launches"""

    async def setup_hook(self):
        ordered = sorted(
            setups,
            key=lambda x: x["priority"]
        )

        for item in ordered:
            fn = item["fn"]
            logger.debug(f"Awaiting function: {fn.__name__}...")
            await fn(self)

def on_startup(*, priority=0):
    """
    Decorator that marks this function to be executed once upon startup of the bot.
    The decorated function must be async and has to take a discord bot as an argument 

    Execution order is based on priority first, then import order second (i.e if your script imports a module that also has a
    function with this decorator then the imported module's function will be executed first as long as they have the same priority).
    """
    def decorator(fn):
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("@on_startup functions must be async")
        
        setups.append({
            "fn": fn,
            "priority": priority,
        })
        logger.debug(f"Registered function: {fn.__name__}")
        return fn
    return decorator

def import_plugins():
    with os.scandir(plugins_path) as mods:
        for mod in sorted(mods, key=lambda m: m.name):
            if not mod.is_dir(): continue
            if mod.name.startswith("_"): continue
            if not os.path.exists(os.path.join(mod.path, "__init__.py")): continue

            try:
                importlib.import_module(f"{src.plugins.__name__}.{mod.name}")
                logger.debug(f"Imported plugin: {mod.name}")
            except Exception as e:
                logger.exception(f"Failed to import plugin: {mod.name}")
