from discord.ext.commands import Context
import random
from datetime import timedelta, datetime, time

from src.pluginbot import sig_setup
from src.signal import Signal
from src.utils import utc_to_ams

from .renderer import render_rollies
from .money_schema import Account
from .interface_db import read_account

sig_rollies = Signal()

@sig_setup.connect
async def setup_commands(client):

    @client.command()
    async def rollies(ctx: Context):
        account = await Account.get_account(ctx.author.id)

        if not account.daily_check(ctx.message.created_at):
            delta_time = time_until_midnight(ctx.message.created_at)
            await ctx.send(f'''
            Bisch wait.
            You can only get money from your roll in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).

            That being said enjoy your gamba:
            ''')

        roll = random.randint(1, 1000)
        account.add_balance(roll)
        await account.save()

        rendered_roll = render_rollies(roll)
        await ctx.reply(rendered_roll)



    @client.command()
    async def balance(ctx: Context):
        ...

    @client.command()
    async def charity(ctx: Context):
        ...

def time_until_midnight(now: datetime) -> timedelta:
    return utc_to_ams(now).time()