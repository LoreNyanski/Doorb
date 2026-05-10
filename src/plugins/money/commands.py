from discord.ext.commands import Context, Bot

from src.pluginbot import sig_setup, resolve_dumbass
from src.signal import Signal

from .renderer import render_rollies, render_balance, render_charity
from .money_schema import Account, do_daily, time_until_midnight, transfer, WithdrawNegativeError, WithdrawNotEnoughBalanceError

sig_rollies = Signal("rollies")

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
        await ctx.send(rendered_roll)

        await sig_rollies.emit(roll)

    @client.command()
    async def balance(ctx: Context, *args):
        match len(args):
            case 0:
                member = ctx.author
            case 1:
                member = resolve_dumbass(ctx, args[0])
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
    async def charity(ctx: Context, *args):
        match len(args):
            case 2:
                member = resolve_dumbass(ctx, args[0])
                if not member:
                    await ctx.send("Couldn't find user lol, try mentioning someone")
                    return
                try: 
                    amount = int(args[1])
                except: 
                    await ctx.send("Amount must be integer :P")
                    return
            case _:
                await ctx.send("Incorrect arguments bub")
                return
        
        sender = await Account.get_account(ctx.author.id)
        recipient = await Account.get_account(member.id)
        now = ctx.message.created_at

        try:
            transaction = await transfer(sender, recipient, amount, now)
        except WithdrawNegativeError:
            await ctx.send('Not today satan')
            return
        except WithdrawNotEnoughBalanceError:
            await ctx.send(f'Cant give what you dont have :pensive:\n(Your balance is: {sender.balance})')
            return
        
        rendered_charity = render_charity(sender)
        await ctx.send(rendered_charity)