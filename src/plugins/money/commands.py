from discord.ext.commands import Context

from src.pluginbot import setup_handler

@setup_handler()
async def setup_commands(client):

    @client.command()
    async def rollies(ctx: Context):
        ...

    @client.command()
    async def balance(ctx: Context):
        ...

    @client.command()
    async def charity(ctx: Context):
        ...