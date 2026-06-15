from discord.ext.commands import Bot, Context
from discord import Message

from src.pluginbot import sig_setup, resolve_dumbass
from src.plugins.incidents import sig_on_incident, Incident
from src.plugins.money import Account

from .backend import BetTable, Bet

current_bet_table = BetTable()

@sig_setup.connect
async def setup_betting_commands(client: Bot):
    
    @client.command()
    async def bet(ctx: Context, *args):
        global current_bet_table
        """Lists all statistics for a set of people"""
        match len(args):
            case 0:
                # DISPLAY BET TABLE WITH CURRENT BET
                ...
            case 2:
                member_arg = str(args[0])
                amount_arg = str(args[1])
                member = resolve_dumbass(ctx.guild, member_arg)
                if not member:
                    await ctx.send('Cant find dumbass with that name (try mentioning someone)')
                    return
                try:
                    amount = int(amount_arg)
                except:
                    await ctx.send('try actually betting a "number"')
                    return
                if amount < 1:
                    await ctx.send('not today satan (try betting a positive integer)')
                    return
                if False: # TODO check if you have enough moneys
                    await ctx.send(f'lmao poor mf :kekw: :index_pointing_at_the_viewier:\n(Your balance is: )')
                    return
                # PLACE BET
                ...
            case _:
                await ctx.send("This command takes 0 or 2 arguments bub")
                return
            
@sig_on_incident.connect
async def on_incident(message: Message):
    payouts = await handle_payouts(message.author.id)
    correct_bettors = []
    for bet, payouts in payouts:
        bettor = resolve_dumbass(message.guild, str(bet.bettor_id))
        if bettor:
            correct_bettors.append(bettor.display_name)
        else:
            correct_bettors.append("Unknown")

    reply = f'''
# BETS OVER!
Correct guessers: {", ".join(correct_bettors)}
{render_bet_table(current_bet_table)}'''



async def handle_payouts(winner_id: int) -> list[tuple[Bet, int]]:
    payouts = current_bet_table.payouts(winner_id)
    for bet, payout in payouts:
        bettor_account = await Account.get_account(bet.bettor_id)
        bettor_account.deposit(payout)
        bettor_account.save()
    return payouts

def render_bet_table(bet_table: BetTable):
    summary = bet_table.summary()
    COL_1_TITLE = "dumbass_candidates"
    COL_2_TITLE = "total bets"
    COL_3_TITLE = "%"
    COL_4_TITLE = "payout odds"

    table_header = f'''
{"":<{len_dumbasses}}  {COL_2_TITLE:>{len_bet_amounts}}  {COL_3_TITLE:>{len_percentages}}  {"":>11}  {COL_4_TITLE:>{len_odds}}
{COL_1_TITLE}
'''
    table = [table_header]

    for subject, data in summary:
        percentage = 1/data["odds"]*100
        bar = '█' + int(percentage/10)*'█'
        row = f'''
{subject:<{len_dumbasses}}  {data["total"]:>{len_bet_amounts}}  {percentage:>{len_percentages}}  {bar:{'▒'}>11}  {data["odds"]:>{len_odds}}
'''
        table.append(row)

    return f'```\n{"\n".join(table)}\n```'