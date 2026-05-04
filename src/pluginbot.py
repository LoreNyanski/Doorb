import logging
import inspect
import os
import importlib
from discord.ext.commands import Bot
import discord

import src.plugins

from .env import TEST_GUILD_ID, TEST_MODE

logger = logging.getLogger(__name__)

plugins_path = src.plugins.__path__[0]

setup_handlers = []
on_message_handlers = []

class PluginBot(Bot):
    """A discord bot that executes all functions registered with the @setup_handler() decorator before it launches"""

    async def setup_hook(self):
        # sort setups
        ordered = sorted(
            setup_handlers,
            key=lambda x: x["priority"])
        
        # call all setups
        for item in ordered:
            fn = item["fn"]
            logger.debug(f"Awaiting function: {fn.__name__}...")
            await fn(self)

    async def on_message(self, message: discord.Message):
        # dont respond to yourself dumbass
        if message.author == self.user: return
        if guild_guard(message.guild.id): return

        # process commands
        await self.process_commands(message)

        # call all message handlers
        for handler in on_message_handlers:
            await handler(message)


## DONT FORGE TO ADD THIS TO THE FRONT OF EVERY SINGLE HANDLER
def guild_guard(guild_id: int):
    """Returns true if the event should not be processed according to test mode. 
    (If test mode is on, only run in the test guild, otherwise run everywhere else)
    """
    logger.debug(f"Comparing guild: {guild_id} to TEST_GUILD: {TEST_GUILD_ID}...")
    if TEST_MODE != (guild_id == TEST_GUILD_ID): return True
    else: return False

def setup_handler(*, priority=0):
    """
    Decorator that marks this function to be executed once upon startup of the bot.
    The decorated function must be async and has to take a discord bot as an argument 

    Execution order is based on priority first, then import order second (i.e if your script imports a module that also has a
    function with this decorator then the imported module's function will be executed first as long as they have the same priority).
    """
    def decorator(fn):
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("@setup_handler functions must be async")
        
        setup_handlers.append({
            "fn": fn,
            "priority": priority,
        })
        logger.debug(f"Registered function: {fn.__name__}")
        return fn
    return decorator

def on_message_handler():
    """
    Decorator that marks this function to be executed once upon message.
    The decorated function must be async
    """
    def wrapper(func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("@setup_handler functions must be async")
        
        on_message_handlers.append(func)
        return func
    return wrapper

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