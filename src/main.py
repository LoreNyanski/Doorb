import logging
import discord

from .pluginbot import PluginBot, import_plugins
from .env import DISCORD_TOKEN

intents = discord.Intents.all()
client = PluginBot(command_prefix="!", intents=intents, help_command=None)

@client.event
async def on_ready():
    print(f'{client.user} has logged in\n\nConnected to the following guilds:')
    for guild in client.guilds:
        print(f'    {guild.name} (id: {guild.id})')

@client.command()
async def hi(ctx):
    await ctx.send('haiii :3')
        
def setup_logging():    
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] | %(name)s : %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    src_logger = logging.getLogger("src")
    src_logger.setLevel(logging.DEBUG)
    src_logger.addHandler(handler)

    src_logger.propagate = False

if __name__ == "__main__":
    setup_logging()
    import_plugins()
    client.run(DISCORD_TOKEN)