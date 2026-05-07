import logging
import inspect
import os
import importlib
from discord.ext.commands import Bot
import discord

import src.plugins

from .env import TEST_GUILD_ID, TEST_MODE
from .signal import Signal

logger = logging.getLogger(__name__)

plugins_path = src.plugins.__path__[0]

sig_setup = Signal("setup")
sig_on_message = Signal("on_message")

class PluginBot(Bot):

    async def setup_hook(self):
        await sig_setup.emit(self)

    async def on_message(self, message: discord.Message):
        # dont respond to yourself dumbass
        if message.author == self.user: return
        if guild_guard(message.guild.id): return

        # process commands
        await self.process_commands(message)

        # call all message handlers
        await sig_on_message.emit(message)


## DONT FORGET TO ADD THIS TO THE FRONT OF EVERY SINGLE EVENT
def guild_guard(guild_id: int):
    """Returns true if the event should not be processed according to test mode. 
    (If test mode is on, only run in the test guild, otherwise run everywhere else)
    """
    if TEST_MODE != (guild_id == TEST_GUILD_ID): return True
    else: return False

def import_plugins():
    with os.scandir(plugins_path) as mods:
        for mod in sorted(mods, key=lambda m: m.name):
            if not mod.is_dir(): continue
            if mod.name.startswith("_"): continue
            if not os.path.exists(os.path.join(mod.path, "__init__.py")): continue

            try:
                importlib.import_module(f"{src.plugins.__name__}.{mod.name}")
                logger.debug(f"Successfully imported plugin: {mod.name}    :D")
            except Exception as e:
                logger.exception(f"Failed to import plugin: {mod.name}    D:")