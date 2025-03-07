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
import discord.ext
import discord.ext.commands
from door_manager import Door_manager
from dotenv import load_dotenv
# from games import

'''
TODO LIST
- Send embeds instead of messages.
- Make statistics more interpretable. (graph)
- on message delete 
- list of all incidents of a user with jump links
- hivemind automatically activates in new channels
- David scale of things
- add custom names
- catlike typing detect
'''

'''
This patch:
- add balance to stats (see whos richest)
- serverstats check the COLLECTIVE streaks and incidents (serverstats mean gives a leaderboard)
- o7 reactor
- catlike typing detected
- some kind of yo mama

- stealing from people (punishment incl.)
  - if possible, lot of punishments
- things to spend money on
  - clown compressing
  - exchange money for @everyone
- elden ring message creator
- !kys

'''


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
shibe = os.getenv('shibe')
filepath = os.getenv('filepath')
test_guild = os.getenv('test_guild')
main_guild = os.getenv('main_guild')
tracked_sticker = os.getenv('tracked_sticker')
test_sticker = os.getenv('test_sticker')

# TODO: proper intents my guy
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

dm = Door_manager()

# -----------------------------------------------------------------------------------------
#                                     Variables
# -----------------------------------------------------------------------------------------


# CONSTANTS
CHANCE_AMOGUS = 15
CHANCE_DAD = 15
CHANCE_FUCKING = 15
CHANCE_HIVEMIND = 2
CHANCE_DUMBASS = 1
REQUIREMENT_HIVEMIND = 3

# Globals
last_message = ''
client.insults = ['Idiot', 'Dumbass', 'Stupid', 'Unintelligent', 'Fool', 'Moron', 'Dummy', 'Daft', 'Unwise', 'Half-baked',
                  'Knobhead', 'Hingedly-impaired', 'Architectually challenged', 'Ill-advised', 'Imbecile', 'Dim', 'Unthinking',
                  'Half-witted', 'Low intelligence specimen']
client.active_sticker = int(tracked_sticker)
# client.active_sticker = int(test_sticker)

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

async def get_all_dumbasses(guild, test=False):
    # if its the test guild and were not testing then don't fetch shit from here
    if str(guild.id) == test_guild and not test:
        print('test guild skipped')
        return
    
    dm.cleardata()
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            async for message in channel.history(limit=None):
                if client.active_sticker in [stckr.id for stckr in message.stickers]:
                    dm.new_dumbass(message.author.id, message.created_at)
            print(channel.name + ' done')
    print('everything done')

async def mods_kill_this_guy(member: discord.Member, channel: discord.TextChannel, reason: str):
    channel.send(f'''
User @<{member.id}>, you have been deemed unworthy of life for the following reason:
{reason}

Any last words?
''')
    # task until they respond or 2 minutes
    member.ban(delete_message_days=0,delete_message_seconds=0, reason="The law")
    channel.send(f"User @<{member.id}> has been banned for 100000 seconds. o7")
    #task to unban them 100000 seconds later
    
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

def format_stats(user: discord.User) -> str:
    raw_stats = dm.stats(user.id, 0, 'self')
    try:
        res = [raw_stats[0]]+[format_deltatime(time) for time in raw_stats[1:]]
    except:
        try:
            res = [raw_stats[0]] + ['   Data needed'] * 4 + [format_deltatime(raw_stats[2])]
        except:
            res = [raw_stats[0]] + ['   Data needed'] * 5
    response = f'''
{user.name}'s stats:
```
Total incidents:  {res[0]:>14}
Avg time between: {res[1]}
Med time between: {res[2]}
Longest  streak:  {res[3]}
Shortest streak:  {res[4]}

Current streak:   {res[5]}
```
'''
    return response

def direct_mentions(message):
    return [user for user in message.mentions if user not in message.reference]

def compress_clown(user, amount):
    dm.add_compr(user.id, amount)
    #apply compression
    #
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

def fucking_check(message) -> bool:
    return re.search(r"\S+ fucking? \S+", message.content, re.IGNORECASE) and rndm(CHANCE_FUCKING)

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

@client.event
async def on_guild_available(guild):
    pass
    # if str(guild.id) not in [main_guild, test_guild]:
        # await guild.leave()

@client.event
async def on_guild_join(guild):
    pass
    # if str(guild.id) not in [main_guild, test_guild]:
        # await guild.leave()
#    await get_all_dumbasses(guild)

@client.event
async def on_message_removed(message):
    pass


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

    elif fucking_check(message):
        words = [i for i in message.content.split() if i != '']
        fuking = [i for i, word in enumerate(words) if re.match(r"fucking?", word, re.IGNORECASE)][0]
        response = words[fuking - 1] + " is doing WHAT to " + words[fuking + 1] + " now???"

        await message.reply(content=response)

    # sticker check
    if door_check(message):
        dm.new_dumbass(message.author.id, message.created_at)
        if rndm(CHANCE_DUMBASS):
            response = random.choice(client.insults)
            await message.reply(response)
        if not dm.no_bets():
            response = str(dm.bets)
            for user_id in dm.bets.get_dumbass_candidates():
                str_id = str(user_id)
                username = f'{client.get_guild(1287871806534848563).get_member(user_id).name:<{len(str_id)}}'
                response = response.replace(str_id, username)
            pays = finish_bet(message.author.id)
            response = '''
# BETS OVER!
Correct guessers: {}'''.format(', '.join([client.get_guild(1287871806534848563).get_member(int(id)).name for id in pays])).replace('_', '\_') + response
        
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
    ams_offset = datetime.timedelta(hours=1)
    today_midnight = (datetime.datetime.now(datetime.timezone.utc)+ams_offset).replace(hour=0,minute=0,second=0,microsecond=0)
    now = ctx.message.created_at+ams_offset
    bt = dm.get_bet(ctx.author.id)
    if not delta_time.days < 0:
        response = f'''
Daily available :D
You're balance: {dm.get_money(ctx.author.id)} *({dm.get_money(ctx.author.id) + bt[1]})*
Current bet: {"None" if bt[0]==0 else client.get_guild(1287871806534848563).get_member(bt[0]).name} {bt[1]}
'''
    else:  
        delta_time = today_midnight - now
        response = f'''
Daily available in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).
You're balance: {dm.get_money(ctx.author.id)} *({dm.get_money(ctx.author.id) + bt[1]})*
Current bet: {"None" if bt[0]==0 else client.get_guild(1287871806534848563).get_member(bt[0]).name} {bt[1]}
'''
    await ctx.send(response)

# Display list of commands
@client.command()
async def help(ctx):
    response = '''
Welcome to doorbot!

I am here to tell you who's the biggest dumbass on your discord server.

List of commands:
- !help - youre reading it rn idiot
- !stats [optional: User ping | mean, median, max, min, count, last] - displays your/someone else's stats or the leaderboard in provided statistic on the server
- !bet [optional:user] [optional:amount] - place a bet on who will be the next dumbass. If none provided displays the current bets
- !balance - how poor you are, who you bet on
- !rollies - gamba

Coming soon™:
- !incidents - a list of timestamps to all of your door check fails
- !woke - youll see
- deleting incidents deleting instances in the database aswell
- more interpretable statistics (lets be honest the current one is crap)
- doorbot messages using embeds instead of textbox
- !kys

Patch notes:
- pingable bet and stats
- no longer float money
- !balance and !bet now shows your current bet
    '''
    
    await ctx.send(response)

# -----------------------------------------------------------------------------------------
#                                   Door shenanigans
# -----------------------------------------------------------------------------------------

@client.command()
async def incidents(ctx, *args):
    pass

# List statistics for yourself
@client.command()
async def stats(ctx, *args):
    if len(args) == 0:
        response = format_stats(ctx.author)
        await ctx.send(response)
        return 
    if len(args) != 1:
        await ctx.send('Invalid arguments lol')
        return
    arg = args[0]
    if ctx.message.mentions:
        response = format_stats(ctx.message.mentions[0])
        await ctx.send(response)
        return 
    elif arg in ['mean', 'count', 'median', 'max', 'min', 'last']:
        stat = arg
        res = dm.stats(ctx.author.id, [member.id for member in ctx.guild.members], stat)
        if stat == 'count':
            res = [(ctx.guild.get_member(user_id).name, str(count)) for user_id, count in res[:10]]
            longest_name = max([len(name) for name,time in res])
        else:
            res = [(ctx.guild.get_member(user_id).name, format_deltatime(time) if not type(time)== str else '    Data needed') 
                   for user_id, time in res[:10]]
            longest_name = max([len(name) for name,time in res])
        response = '\n'.join(['#{0:<2}  {1:<{2}} {3:<}'.format(index+1, tup[0], longest_name, tup[1]) for index, tup in enumerate(res)])
        response = '```\n' + response + '\n```'
        match stat:
            case 'mean': response = 'Average time between incidents:' + response
            case 'count': response = 'Total number of incidents:' + response
            case 'median': response = 'Median of time between incidents:' + response
            case 'max': response = 'Longest streak without incidents:' + response
            case 'min': response = 'Shortest streak without incidents:' + response
            case 'last': response = 'Current streaks:' + response
        await ctx.send(response)
        return
    else:   
        await ctx.send('thats not a real statistic ._. \n check your own stats for options')
        return

# allows you to place bets on who will be the next to fail an int check
@client.command()
async def bet(ctx, *args):
    if len(args) == 0:
        bt = dm.get_bet(ctx.author.id)
        response = f'Your bet: {"None" if bt[0]==0 else client.get_guild(1287871806534848563).get_member(bt[0]).name} {bt[1]}\n'
        response = str(dm.bets)
        for user_id in dm.bets.get_dumbass_candidates():
            user_id =int(user_id)
            str_id = str(user_id)
            username = f'{client.get_guild(1287871806534848563).get_member(user_id).name:<{len(str_id)}}'
            response = response.replace(str_id, username)

        await ctx.send(response)
        # display current bets

    elif len(args) == 2:
        try:
            if ctx.message.mentions:
                user = ctx.message.mentions[0]
            else:
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

# daily roll between 1 and 1000 - make it look like the google rng - 
@client.command()
async def rollies(ctx: discord.ext.commands.Context):
    ams_offset = datetime.timedelta(hours=1)
    today_midnight = (datetime.datetime.now(datetime.timezone.utc)+ams_offset).replace(hour=0,minute=0,second=0,microsecond=0)
    lastd = dm.get_last_daily(ctx.author.id)+ams_offset
    now = ctx.message.created_at+ams_offset
    
    delta_time = today_midnight - lastd
    result = random.randint(1, 1000)
    if not delta_time.days < 0:
        dm.daily(ctx.author.id, result, ctx.message.created_at)
        print('money added')
    else:
        # delta_time = datetime.timedelta(days=1) - delta_time
        delta_time = today_midnight - now
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

@client.command
async def clown(ctx, *args):
    if len(args) > 1:
        await ctx.send("Invalid arguments lol")
        return
    compression = 0
    if len(args) == 1:
        if type(args[0]) == int:
            compression = args[0]
            if compression < 0:
                await ctx.send("# YOU SHALL NOT *UN*-COMPRESS THE CLOWN")
                return
        elif args[0] is "origin":
            original = True
            #display original clown           
        else:
            await ctx.send("Invalid arguments lol")
            return
    if money_check(author_id, compression):
        dm.add_money(author_id, compression*-1)
        compress_clown()
    else:
        ctx.send("Imagine being too poor to compress clowns.\nWouldn't wanna to be you mate")

# @client.command
# async def woke_trivia(ctx):

# @client.command()
# async def wild_magic(ctx):

# @client.command()
# async def scp():

# Run the client
if __name__ == "__main__":
    client.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)




