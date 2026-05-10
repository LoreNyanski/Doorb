from discord.ext.commands import Context, Bot
from datetime import timedelta, datetime

from src.pluginbot import sig_setup, resolve_dumbass
from src.signal import Signal
from src.utils import utc_to_ams

from .renderer import render_rollies, render_balance
from .money_schema import Account, do_daily, time_until_midnight

sig_rollies = Signal()

@sig_setup.connect
async def setup_commands(client: Bot):

    @client.command()
    async def rollies(ctx: Context):
        account = await Account.get_account(ctx.author.id)
        now = ctx.message.created_at

        success, roll = await do_daily(account, now)

        if not success:
            delta_time = time_until_midnight(now)
            await ctx.send(f'''
            Bisch wait.
            You can only get money from your roll in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).

            That being said enjoy your gamba:
            ''')

        rendered_roll = render_rollies(roll)
        await ctx.reply(rendered_roll)

        sig_rollies.emit(roll)

    @client.command()
    async def balance(ctx: Context, *args):
        match len(args):
            case 0:
                member = ctx.author
            case 1:
                member = resolve_dumbass(args[0])
                if not member:
                    await ctx.send("Couldn't find user lol, try mentioning someone")
                    return
            case _:
                await ctx.send("Too many arguments bub")
                return
        
        account = await Account.get_account(member.id)
        now = ctx.message.created_at

        rendered_balance = render_balance(account, now)
        await ctx.send(rendered_balance)

    @client.command()
    async def charity(ctx: Context):
        ...