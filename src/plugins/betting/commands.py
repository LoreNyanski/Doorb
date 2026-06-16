from discord.ext.commands import Bot, Context
from discord import Message, Guild

from src.pluginbot import sig_setup, resolve_dumbass
from src.plugins.incidents import sig_on_incident, Incident
from src.plugins.money import Account, WithdrawNotEnoughBalanceError, WithdrawNegativeError

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
                reply = f'''
Current bet: {render_single_bet(get_current_bet(ctx.author.id))}
{render_bet_table(ctx.guild, current_bet_table)}
'''
                await ctx.send(reply)
            case 2:
                member_arg = str(args[0])
                amount_arg = str(args[1])
                member = resolve_dumbass(ctx.guild, member_arg)
                if not member:
                    await ctx.send('Cant find dumbass with that name (try mentioning someone)')
                    return
                try:
                    amount = int(amount_arg)
                except ValueError:
                    await ctx.send('try actually betting a "number"')
                    return
                # REGISTER BET WITH PERSON, IF ALREADY HAVE A BET, REPLACE
                try:
                    account = await Account.get_account(member.id)
                    account.withdraw(amount)
                except WithdrawNegativeError:
                    await ctx.send('not today satan (try betting a positive integer)')
                    return
                except WithdrawNotEnoughBalanceError:
                    await ctx.send(f'lmao poor mf :kekw: :index_pointing_at_the_viewier:\n(Your balance is: )')
                    return
                except:
                    await ctx.send('Unknown error lmao')
                    return
            case _:
                await ctx.send("This command takes 0 or 2 arguments bub")
                return

def get_current_bet(dumbass_id) -> Bet:
    ...
    #TODO

@sig_on_incident.connect
async def on_incident(message: Message):
    payouts = await handle_payouts(message.author.id)
    correct_bettors = []
    for bet, payout in payouts:
        bettor = resolve_dumbass(message.guild, str(bet.bettor_id))
        if bettor:
            correct_bettors.append(bettor.display_name)
        else:
            correct_bettors.append("Unknown")
    reply = f'''
# BETS OVER!
Correct guessers: {", ".join(correct_bettors)}
{render_bet_table(current_bet_table)}'''
    await message.channel.send(reply)


async def handle_payouts(winner_id: int) -> list[tuple[Bet, int]]:
    payouts = current_bet_table.payouts(winner_id)
    for bet, payout in payouts:
        bettor_account = await Account.get_account(bet.bettor_id)
        bettor_account.deposit(payout)
        bettor_account.save()
    return payouts

def render_single_bet(guild: Guild, bet: Bet):
    subject = resolve_dumbass(guild, str(bet.subject_id))
    return f'{subject.name} {bet.amount}'

def render_bet_table(guild: Guild, bet_table: BetTable):
    summary = bet_table.summary()
    COL_1_TITLE = "dumbass_candidates"
    COL_2_TITLE = "total bets"
    COL_3_TITLE = "%"
    COL_4_TITLE = "payout odds"

    subject_names = []
    amounts = []
    percentages = []
    odds = []
    for subject_id, data in summary.items():
        subject = resolve_dumbass(guild, str(subject_id))
        subject_names.append(subject.name)
        amounts.append(f'{data["total"]}')
        percentage = 1/data["odds"]*100
        percentages.append(f'{percentage:.1f}')
        odds.append(f'{data["odds"]:.1f}')

    len_dumbasses = max(len(COL_1_TITLE), [len(x) for x in subject_names])
    len_bet_amounts = max(len(COL_2_TITLE), [len(x) for x in amounts])
    len_percentages = max(len(COL_3_TITLE), [len(x) for x in percentages])
    len_odds = max(len(COL_4_TITLE), [len(x) for x in odds])

    table_header = f'''
{"":<{len_dumbasses}}  {COL_2_TITLE:>{len_bet_amounts}}  {COL_3_TITLE:>{len_percentages}}  {"":>11}  {COL_4_TITLE:>{len_odds}}
{COL_1_TITLE}
'''
    table = [table_header]

    for i in range(len(subject_names)):
        bar = '█' + int(percentages[i]/10)*'█'
        row = f'''
{subject_names[i]:<{len_dumbasses}}  {amounts[i]:>{len_bet_amounts}}  {percentages[i]:>{len_percentages}}  {bar:{'▒'}>11}  {odds[i]:>{len_odds}}
'''
        table.append(row)

    return f'```\n{"\n".join(table)}\n```'