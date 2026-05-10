from discord.ext.commands import Context
from datetime import timedelta, datetime

from src.pluginbot import sig_setup, PluginBot
from src.signal import Signal
from src.utils import utc_to_ams

from .renderer import render_rollies
from .money_schema import Account, do_daily

sig_rollies = Signal()

@sig_setup.connect
async def setup_commands(client: PluginBot):

    @client.command()
    async def rollies(ctx: Context):
        account = await Account.get_account(ctx.author.id)
        timestamp = ctx.message.created_at

        success, roll = await do_daily(account, timestamp)

        if not success:
            delta_time = time_until_midnight(timestamp)
            await ctx.send(f'''
            Bisch wait.
            You can only get money from your roll in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).

            That being said enjoy your gamba:
            ''')

        rendered_roll = render_rollies(roll)
        await ctx.reply(rendered_roll)

        sig_rollies.emit(roll)



    @client.command()
    async def balance(ctx: Context):

        ...

    @client.command()
    async def charity(ctx: Context):
        ...

def time_until_midnight(now: datetime) -> timedelta:
    return utc_to_ams(now).time()