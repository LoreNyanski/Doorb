# VSCode terminal reminders lmao
# minimise terminal - ctrl + j
# interrupt terminal - ctrl + c

# bot.py
import os
import re
import discord
import random
import logging
import datetime

from time import sleep
from discord.ext import commands
from door_manager import Door_manager
from dotenv import load_dotenv
# from games import



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
shibe = os.getenv('shibe')
filepath = os.getenv('filepath')

# TODO: proper intents my guy
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

dm = Door_manager()

# -----------------------------------------------------------------------------------------
#                                     Variables
# -----------------------------------------------------------------------------------------


# CONSTANTS
CHANCE_AMOGUS = 5
CHANCE_DAD = 5
CHANCE_HIVEMIND = 2
CHANCE_DUMBASS = 2
REQUIREMENT_HIVEMIND = 3

# Globals
last_message = ''
client.insults = ['Idiot', 'Dumbass', 'Stupid', 'Unintelligent', 'Fool', 'Moron', 'Dummy', 'Daft', 'Unwise', 'Half-baked',
                  'Knobhead', 'Hingedly-impaired', 'Architectally challenged', 'Ill-advised', 'Imbecile', 'Dim', 'Unthinking', 'Half-witted']
# client.active_sticker = 1305957931304615997

# this is a test sticker
client.active_sticker = 1321199183851687966 

# -----------------------------------------------------------------------------------------
#                                    Functions
# -----------------------------------------------------------------------------------------


# Given an int 'chance' returns true with 1/chance probability 
def rndm(chance) -> bool:
    if chance < 1: return False
    return random.randint(1,chance) == 1
    
def finish_bet(correct_id) -> dict:
    pay = dm.bets.get_payouts(correct_id)
    for user_id in pay:
        dm.add_money(user_id, pay[user_id])
    dm.clearbets()
    return pay

async def get_all_dumbasses(guild):
    dm.cleardata()
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            async for message in channel.history(limit=None):
                if client.active_sticker in [stckr.id for stckr in message.stickers]:
                    dm.new_dumbass(message.author.id, message.created_at)
            print(channel.name + ' done')
    print('everything done')
            
def format_deltatime(time: datetime.timedelta) -> str:
    days = time.days
    hours = time.seconds // 3600
    minutes = time.seconds % 3600 // 60
    seconds = time.seconds % 3600 % 60

    ret = ''
    ret += f'{days:>2}d ' if days > 0 else '    '
    ret += f'{hours:>2}h ' if hours > 0 or days > 0 else '    '
    ret += f'{minutes:>2}m ' if minutes > 0 or hours > 0 or days > 0 else '    '
    ret += f'{seconds:>2}s'
    
    return ret


# -----------------------------------------------------------------------------------------
#                                    Predicates
# -----------------------------------------------------------------------------------------


# Better version of hivemind. Shouldn't just check the last 3 messages but if the same message was said
# 3 times in the past idk 10 seconds. Also doesnt send the message if it has already done so
def hivemind_check(message, last_msg, lst) -> bool:
    if len(lst) == 0 or last_msg == message.content: return False
    first = message.content
    return all(first==i.content for i in lst) and rndm(CHANCE_HIVEMIND)

def amogus_check(message) -> bool:
    return re.search(r'.*a.*m.*o.*g.*u.*s.*', message.content, re.IGNORECASE) and not re.search(r'.*amogus.*', message.content, re.IGNORECASE) and rndm(CHANCE_AMOGUS)

def dad_check(message) -> bool:
    return re.search(r"^I('| a)?m ", message.content, re.IGNORECASE) and rndm(CHANCE_DAD)

def door_check(message) -> bool:
    if message.stickers:
        return client.active_sticker in [stckr.id for stckr in message.stickers]
    else: return False


# -----------------------------------------------------------------------------------------
#                                    Events
# -----------------------------------------------------------------------------------------

# Error "handler"
# @client.event
# async def on_error(event, *args, **kwargs):
    # print(f'I just shat myself at {event}')

# On ready handler
@client.event
async def on_ready():
    print(f'{client.user} has logged in\n\nConnected to the following guilds:')
    for guild in client.guilds:
        print(f'    {guild.name} (id: {guild.id})')
        # await get_all_dumbasses(guild)

# @client.event
# async def on_guild_available(guild):
    # await get_all_dumbasses(guild)

# Message handler
@client.event
async def on_message(message):
    global last_message

    # Dont respond to your own message idiot
    if message.author == client.user:
        last_message = message.content
        return

    # Do commands if applicable
    await client.process_commands(message)

    # Test feature
    if message.content == 'door':
        await message.channel.send("look at this dumbass XD")

    # Amogus detector
    if amogus_check(message):
        msg = message.content.replace('||','')
        response = '||'
        for i in 'amogus':
            indx = msg.lower().find(i)
            response += msg[:indx]
            response += '||' + msg[indx] + '||'
            msg = msg[indx+1:]
        response += msg + '||'

        await message.reply(content=response.replace('||||',''))

    # Dad bot feature
    elif dad_check(message):
        pattern = re.compile(r"^I('| a)?m ", re.IGNORECASE)
        msg = message.content
        response = 'Hi '
        response += re.sub(pattern, '', msg).strip()
        response += ", I'm dad :D"

        await message.channel.send(content=response, reference=message.to_reference())

    # Hivemind
    elif hivemind_check(message, last_message, [msgs async for msgs in message.channel.history(limit=REQUIREMENT_HIVEMIND)]):
        msg = message.content
        response = msg

        await message.channel.send(content=response)



    # sticker check
    if door_check(message):
        dm.new_dumbass(message.author.id, message.created_at)
        if rndm(CHANCE_DUMBASS):
            response = random.choice(client.insults)
            message.reply(response)
        if not dm.no_bets():
            response = str(dm.bets)
            pays = finish_bet(message.author.id)
            response = '''
# BETS OVER!
Correct guessers: {}
'''.format(', '.join([message.guild.get_member(id).name for id in pays])) + response
        
            await message.channel.send(content=response)






# -----------------------------------------------------------------------------------------
#                                    Meta commands
# -----------------------------------------------------------------------------------------

# Test command
@client.command(name='hi')
async def hi(ctx):
    await ctx.send('haiii :3')

@client.command()
async def balance(ctx):
    delta_time = dm.get_delta_daily(ctx.author.id)
    if delta_time.days > 1:
        response = f'''
Daily available :D
You're balance: {dm.get_money(ctx.author.id)}
'''
    else:  
        delta_time = datetime.timedelta(days=1) - delta_time
        response = f'''
Daily available in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).
You're balance: {dm.get_money(ctx.author.id)}
'''
    await ctx.send(response)

# Display list of commands
@client.command()
async def help(ctx):
    response = '''
Welcome to doorbot!

I am here to tell you who's the biggest dumbass on your discord server.

List of commands:
    help - youre reading it rn idiot
    stats [optional: statistic] - displays your stats or the leaderboard in provided statistic on the server
    bet [optional:user] [optional:amount] - place a bet on who will be the next dumbass. If none provided displays the current bets
    rollies - gamba
    '''
    
    await ctx.send(response)

# -----------------------------------------------------------------------------------------
#                                   Door shenanigans
# -----------------------------------------------------------------------------------------

# List statistics for yourself
@client.command()
async def stats(ctx, *args):
    if len(args) == 0:
        # TODO: time since last incident
        res = dm.stats(ctx.author.id, 0, 'self')
        res = [res[0]]+[format_deltatime(time) for time in res[1:]]
        response = f'''
{ctx.author.name}'s stats:
```
Total incidents:  {res[0]:>14}
Avg time between: {res[1]}
Med time between: {res[2]}
Longest  streak:  {res[3]}
Shortest streak:  {res[4]}

Current streak:   {res[5]}
```
'''
        await ctx.send(response)
        return 
    if len(args) != 1:
        await ctx.send('Invalid arguments lol')
        return
    stat = args[0]
    if stat in ['mean', 'count', 'median', 'max', 'min', 'last']:
        res = dm.stats(ctx.author.id, [member.id for member in ctx.guild.members], stat)
        if stat == 'count':
            res = [(ctx.guild.get_member(user_id).name, str(count)) for user_id, count in res[:10]]
            longest_name = max([len(name) for name,time in res])
        else:
            res = [(ctx.guild.get_member(user_id).name, format_deltatime(time) if not type(time)== str else '    Data needed') 
                   for user_id, time in res[:10]]
            longest_name = max([len(name) for name,time in res])
        response = '\n'.join(['#{0}  {1:<{2}} {3:<}'.format(index+1, tup[0], longest_name, tup[1]) for index, tup in enumerate(res)])
        response = '```\n' + response + '\n```'
        match stat:
            case 'mean': response = 'Average time between incidents:' + response
            case 'count': response = 'Total number of incidents:' + response
            case 'median': response = 'Median of time between incidents:' + response
            case 'max': response = 'Longest streak without incidents:' + response
            case 'min': response = 'Shortest streak without incidents:' + response
            case 'last': response = 'Current streak without incidents:' + response
        await ctx.send(response)
        return
    else:   
        await ctx.send('thats not a real statistic ._. \n check your own stats for options')
        return

# allows you to place bets on who will be the next to fail an int check
@client.command()
async def bets(ctx, *args):
    if len(args) == 0:
        await ctx.send(str(dm.bets))
        # display current bets

    elif len(args) == 2:
        try:
            user = ctx.guild.get_member_named(str(args[0]))
            bet_amount = int(args[1])
        except:
            await ctx.send('Invalid arguments lol')
            return
        if user == None:
            await ctx.send('No user with that name')
            return 
        if user == ctx.author:
            await ctx.send("Can't bet on yourself idiot")
            return
        if bet_amount < 0:
            await ctx.send('not today satan')
            return
        if dm.get_money(ctx.author.id) + dm.get_bet(ctx.author.id)[1] < bet_amount:
            await ctx.send(f'lmao poor mf :kekw: :index_pointing_at_the_viewier:\n(Your balance is: {dm.get_money(ctx.author.id)})')
            return
        
        dm.place_bet(ctx.author.id, user.id, bet_amount)
        await ctx.send(f'Bet successfully placed on {user.name}\n(New balance: {dm.get_money(ctx.author.id)})')
        return
    
    else:
        await ctx.send('Invalid arguments lol')
        return

# -----------------------------------------------------------------------------------------
#                                        Misc
# -----------------------------------------------------------------------------------------

# just straight up blackjack
# async def blackjack(ctx):
    # response = '''
# You fool, you buffoon, you thought I already implemented this?? 
    # - Lore
# '''
    # await ctx.send(response)

# daily roll between 1 and 1000 - make it look like the google rng - 
@client.command()
async def rollies(ctx):
    delta_time = dm.get_delta_daily(ctx.author.id)
    result = random.randint(1, 1000)
    if delta_time.days > 1:
        dm.daily(ctx.author.id, result)
    else:
        delta_time = datetime.timedelta(days=1) - delta_time
        response = f'''
Bisch wait.
You can only get money from your roll in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).

That being said enjoy your gamba:
        '''
        await ctx.send(response)
    response = f'''
```
                Min: 
                1
{result}
                Max: 
                1000

####################
##### Generate #####
####################
```
'''
    await ctx.send(response)
    if result == 1000:
        sleep(0.8)
        await ctx.send('HOLY SHIIIT')
        sleep(0.5)
        await ctx.send(f'<@{shibe}>')
        sleep(1)
        await ctx.send(f'IT FINALLY HAPPENED!!1! <@{shibe}>')
        sleep(0.4)
        await ctx.send(f'<@{shibe}>')
        sleep(1.1)
        await ctx.send(f'you owe me a cookie :D')
    return

# @client.command
# async def woke_trivia(ctx):
    # response = '''
# You fool, you buffoon, you thought I already implemented this?? 
    # - Lore
# '''
    # await ctx.send(response)

# @client.command()
# async def wild_magic(ctx):

# @client.command()
# async def scp():

# Run the client
if __name__ == "__main__":
    client.run(TOKEN, log_handler=handler)