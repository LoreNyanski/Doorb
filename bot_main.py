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
import functools

from time import sleep
from discord.ext import commands
import discord.ext
import discord.ext.commands
from door_manager import Door_manager
from ai import *
from dotenv import load_dotenv
# from games import

load_dotenv()
TEST_MODE = True

TOKEN = os.getenv('DISCORD_TOKEN')
shibe = os.getenv('shibe')
me = os.getenv('me')

test_guild = os.getenv('test_guild')
main_guild = os.getenv('main_guild')
tracked_sticker = os.getenv('tracked_sticker')
test_sticker = os.getenv('test_sticker')

# TODO: proper intents my guy
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

webhook_cache = {}

dm = Door_manager()

# -----------------------------------------------------------------------------------------
#                                     Variables
# -----------------------------------------------------------------------------------------


# CONSTANTS
# I should have done these with dictionaries
CHANCE_AMOGUS = 15
CHANCE_DAD = 15
CHANCE_FUCKING = 15
CHANCE_HIVEMIND = 2
CHANCE_DUMBASS = 1
CHANCE_SALUTE = 2

REQUIREMENT_HIVEMIND = 3

LENGTH_PUNISHMENT = datetime.timedelta(minutes=30)

COST_EVERYONE = 1000 # ignore the fact that this isn't a constant
COST_COOKIE = 10000

COOLDOWN_KYS = datetime.timedelta(minutes=30)
COOLDOWN_EVERYONE = datetime.timedelta(hours=24)
COOLDOWN_STEAL = datetime.timedelta(hours=6)

TIME_PERFECT_GUARDS = datetime.timedelta(minutes=5)
TIME_IMPERFECT_GUARD = datetime.timedelta(minutes=10)

AMS_OFFSET = datetime.timedelta(hours=2) # fucking daylight savings
# I KNOW THERES A BETTER WAY TO DO THIS IM JUST TOO LAZY

# Globals
last_message = ''
client.insults = ['Idiot', 'Dumbass', 'Stupid', 'Unintelligent', 'Fool', 'Moron', 'Dummy', 'Daft', 'Unwise', 'Half-baked',
                  'Knobhead', 'Hingedly-impaired', 'Architectually challenged', 'Ill-advised', 'Imbecile', 'Dim', 'Unthinking',
                  'Half-witted', 'Low intelligence specimen'] # particularly fond of Architectually challenged

client.active_sticker = int(tracked_sticker)
client.active_guild = int(main_guild)

if TEST_MODE:
    client.active_sticker = int(test_sticker)
    client.active_guild = int(test_guild)

# -----------------------------------------------------------------------------------------
#                                    Functions
# -----------------------------------------------------------------------------------------


# Probably not the greatest solution but i like it. 
def guild_restriction(func):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):

        ctx = args[0] if args else None
        guild_id = None

        if isinstance(ctx, commands.Context) or isinstance(ctx, discord.Message):
            guild_id = ctx.guild.id if ctx.guild else None

        if guild_id != client.active_guild:
            return
        
        return await func(*args, **kwargs)
        
    return wrapper



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
    # if its the test guild and were not testing then don't fetch shit from here
    if TEST_MODE:
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
    if isinstance(user, discord.User) or isinstance(user, discord.Member):
        raw_stats = dm.stats(user.id, 0, 'self')
    else:
        raw_stats = dm.serverstats([member.id for member in user.members])
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

async def process_punishments(message: discord.Message) -> bool:
    punishm = dm.get_punishment(message.author.id)
    if punishm:
        (p_type, start, length) = punishm

        if (start + length > datetime.datetime.now(datetime.timezone.utc)):
            #had some help from GPT here, sorry, im in a time crunch :(

            try:

                if not message.content == '':
                    await message.delete()
                    msgreference = message.reference

                    newmsg = textGenerate(personality=p_type, message=message.content)

                    if (msgreference and msgreference.resolved and isinstance(msgreference.resolved, discord.Message)):
                        if msgreference.resolved.webhook_id:                   
                            reply_id = message.guild.get_member_named(msgreference.resolved.author.display_name).id
                        else:
                            reply_id = msgreference.resolved.author.id
                        cont = (f'> <@{reply_id}>: ' + msgreference.jump_url + '\n' + newmsg) 
                    else: 
                        cont = newmsg

                    webhook = await get_webhook(message.channel)

                    await webhook.send(
                        content=cont,
                        username=message.author.display_name,
                        avatar_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url,
                    )
                else:
                    return False
        
            except Exception as e:
                print(f"Error: {e}")
            
            return True
    else:
        return False

async def punish(user_id, channel, reason):
    p_type = random.choice(list(punishments.keys()))
    dm.add_punishment(user_id, p_type, datetime.datetime.now(tz=datetime.timezone.utc), LENGTH_PUNISHMENT)
    await channel.send(f'''
User <@{user_id}>, you have been deemed unworthy of free speech for the following reason:
{reason}

You are only allowed to speak in {p_type} for approximately {LENGTH_PUNISHMENT.seconds//60} minutes
''')

async def get_webhook(channel) -> discord.Webhook:
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]

    webhooks = await channel.webhooks()
    if webhooks:
        webhook = webhooks[0]
    else:
        webhook = await channel.create_webhook(name="PunishmentEnforcer")
    
    webhook_cache[channel.id] = webhook
    return webhook

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

def salute_check(message) -> bool:
    return re.search(r"(general|major|lieutenant|captain|colonel) \S+", message.content, re.IGNORECASE) and rndm(CHANCE_SALUTE)

def door_check(message) -> bool:
    if message.stickers:
        return client.active_sticker in [stckr.id for stckr in message.stickers]
    else: return False

def money_check(user, amount) -> bool:
    return dm.get_money(user.id) >= amount

def can_redeem(user, item, cooldown):
    time: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)
    key = (user.id, item)
    if key not in dm.shop:
        return (True, 0)
    else:
        last_time: datetime.datetime = dm.shop[key]
        boolean = (time - last_time) >= cooldown ## TODO this might be fucked
        return (boolean, last_time)
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
@guild_restriction
async def on_message_removed(message):
    if door_check(message):
    # TODO IF IT WAS A STICKER MESSAGE THEN REMOVE THE INCIDENT
        pass

@client.event
@guild_restriction
async def on_message_edit(before, after):
    await client.process_commands(after)

@client.event
async def on_raw_reaction_add(payload:discord.RawReactionActionEvent):
    # fetching message
    channel = client.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)

    # check for correct reaction and msg
    if str(payload.emoji.name) == '❌':
        if message.webhook_id:
            if message.guild.get_member_named(message.author.display_name).id == payload.user_id: 
                await message.delete()

@client.event
async def on_command(ctx):
    pass
    # print('lmao')

# Message handler
@client.event
@guild_restriction
async def on_message(message: discord.Message):
    global last_message

    # Dont respond to your own message idiot
    if message.author == client.user:
        last_message = message.content
        return

    # Do commands if applicable
    if not message.content.startswith('!'):
        if await process_punishments(message): return
    
    await client.process_commands(message)

    # Test feature
    if message.content == 'door':
        await message.channel.send("look at this dumbass XD")

    # Amogus detector
    # TODO: make it detect even more amogus
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

    # fucking feature
    elif fucking_check(message):
        words = [i for i in message.content.split() if i != '']
        fuking = [i for i, word in enumerate(words) if re.match(r"fucking?", word, re.IGNORECASE)][0]
        response = words[fuking - 1] + " is doing WHAT to " + words[fuking + 1] + " now???"

        await message.reply(content=response)

    # Salute react
    elif salute_check(message):
        await message.add_reaction('🫡')

    # sticker check
    if door_check(message):
        time = message.created_at - dm.get_all_last_incident([member.id for member in message.guild.members])
        dm.new_dumbass(message.author.id, message.created_at)
        response = ''
        if rndm(CHANCE_DUMBASS):
            response = random.choice(client.insults) + '\nYou ruined a ' + format_deltatime(time) + ' long streak >:('
            await message.reply(response)
        if not dm.no_bets():
            response = str(dm.bets)
            for user_id in dm.bets.get_dumbass_candidates():
                str_id = str(user_id)
                username = f'{client.get_guild(client.active_guild).get_member(user_id).name:<{len(str_id)}}'
                response = response.replace(str_id, username)
            pays = finish_bet(message.author.id)
            response = '''
# BETS OVER!
Correct guessers: {}'''.format(', '.join([client.get_guild(client.active_guild).get_member(int(id)).name for id in pays])).replace('_', '\_') + response
        
            await message.channel.send(content=response)



# -----------------------------------------------------------------------------------------
#                                    Meta commands
# -----------------------------------------------------------------------------------------

# Test command
@client.command(name='hi')
@guild_restriction
async def hi(ctx:discord.ext.commands.Context):
    await ctx.send('haiii :3')
    p_type = random.choice(list(punishments.keys()))
    p_time = datetime.timedelta(minutes=1)
    dm.add_punishment(ctx.author.id, p_type, ctx.message.created_at, p_time)
    await ctx.send(f'punishment {p_type} succesfully added for {p_time}')
    #TODO REMOVE THIS IN FINAL VERSION
    

@client.command(name='balance')
@guild_restriction
async def balance(ctx):
    delta_time = dm.get_delta_daily(ctx.author.id)
    today_midnight = (datetime.datetime.now(datetime.timezone.utc)+AMS_OFFSET).replace(hour=0,minute=0,second=0,microsecond=0)
    now = ctx.message.created_at+AMS_OFFSET
    bt = dm.get_bet(ctx.author.id)
    if not delta_time.days < 0:
        response = f'''
Daily available :D
You're balance: {dm.get_money(ctx.author.id)} *({dm.get_money(ctx.author.id) + bt[1]})*
Current bet: {"None" if bt[0]==0 else client.get_guild(client.active_guild).get_member(bt[0]).name if client.get_guild(client.active_guild).get_member(bt[0]) else "None"} {bt[1]}
'''
    else:  
        delta_time = today_midnight - now
        response = f'''
Daily available in {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s).
You're balance: {dm.get_money(ctx.author.id)} *({dm.get_money(ctx.author.id) + bt[1]})*
Current bet: {"None" if bt[0]==0 else client.get_guild(client.active_guild).get_member(bt[0]).name if client.get_guild(client.active_guild).get_member(bt[0]) else "None"} {bt[1]}
'''
    await ctx.send(response)

# Display list of commands
@client.command(name='help')
@guild_restriction
async def help(ctx):
    response = f'''
Welcome to doorbot! 
I am here to tell you who's the biggest dumbass on your discord server.

List of commands:
- !help - youre reading it rn idiot
- !patch - patch notes for the most recent update
- !stats [optional: @user, server, mean, median, max, min, count, last, balance] - displays your/someone else's stats | the server's collective stats | the leaderboard in provided statistic on the server
- !bet [optional: (@)user amount] - place a bet on who will be the next dumbass. If none provided displays the current bets
- !rollies - gamba
- !balance - how poor you are, who you bet on
NEW:
- !buy [optional: thing] - lets you buy things with your money. Otherwise displays available purchases.
- !charity [(@)user amount] - be a benevolent god
- !steal [user] - lets you take money from others.
- !guards - GUAAAAAAARDS!! punish people who tried to steal from you in the past 15 mins
- !kys [@user] - settle arguments with style, a 50/50 with a twist. It also works if you just reply to someone
'''
    
    await ctx.send(response)

@client.command(name='patch')
@guild_restriction
async def patch(ctx):
    response = f'''
Patch notes:
- added !patch
- editing a message now processes commands 
- drastically decreased punishment length (it got old very quickly)
- tweaked purchase values
- fixed pouch showing up as float (this one might come back idk)
- fixed stickers not working under punishment
- fixed !stats balance not working
- reacting X to a punishment message now deletes it
- replying to a punishment message now correctly replies
- minor fixes
'''

    await ctx.send(response)
# -----------------------------------------------------------------------------------------
#                                   Door shenanigans
# -----------------------------------------------------------------------------------------

@client.command(name='buy')
@guild_restriction
async def buy(ctx: commands.Context, *args):
    global COST_EVERYONE
    dex_current, pouch_current = dm.get_steal_stats(ctx.author.id)
    dex_cost = 1000 + 500*dex_current
    pouch_cost = 1000 + 500*pouch_current
    if len(args) == 0:
        # get relevant stats from dm
        await ctx.send(f'''
Syntax: !buy [thing] [optional: other parameters]
Things (the cost is in {{}}):
- everyone {{{COST_EVERYONE}}} - ping everyone. This will *surely* not get annoying very fast
- increase_everyone [new cost] {{new cost}} - increase the cost of pinging eveyrone cuz honestly fuck that. NB: YOU *WILL* HAVE TO PAY AS MUCH AS THE COST YOU'RE TRYING TO SET IT TO
- dex {{{dex_cost}}} - +1 to succeeding a steal, cost increases after each purchase (current: +{dex_current})
- pouch {{{pouch_cost}}} - +1% money stolen, cost increases after each purchase (current: +{pouch_current}%)
- ookie {{{COST_COOKIE}}} - Lore will buy you a cookie unlike *someone*
                       ''')
        return
    else:
        arg = args[0].lower() if isinstance(args[0], str) else args[0]
        match arg:
            case 'dex':
                if not money_check(ctx.author, dex_cost):
                    await ctx.send('cashless behaviour')
                    return
                dm.add_money(ctx.author.id, -1*dex_cost)
                dm.increase_dex(ctx.author.id)
                await ctx.send(f'purchase successful (New DEX: +{dex_current+1})')
            case 'pouch':
                if not money_check(ctx.author, pouch_cost):
                    await ctx.send('cashless behaviour')
                    return
                dm.add_money(ctx.author.id, -1*pouch_cost)
                dm.increase_pouch(ctx.author.id)
                await ctx.send(f'purchase successful (New POUCH: +{pouch_current+1}%)')
            case 'everyone':
                if not money_check(ctx.author, COST_EVERYONE):
                    await ctx.send('cashless behaviour')
                    return
                redeemable, tim = can_redeem(ctx.author, 'everyone', COOLDOWN_EVERYONE)
                if not redeemable:
                    now = datetime.datetime.now(datetime.timezone.utc)
                    delta_time = (tim + COOLDOWN_EVERYONE) - now
                    await ctx.send(f'yeah right. As if i would let you ping eveyrone more than once in 24 hrs (cd: {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s))')
                    return
                dm.add_money(ctx.author.id, -1*COST_EVERYONE)
                dm.shop[(ctx.author.id,'everyone')] = datetime.datetime.now(datetime.timezone.utc)
                await ctx.send('@everyone')
            case 'increase_everyone':
                if not len(args) == 2:
                    await ctx.send('Invalid arguments lol')
                    return
                try:
                    new_cost = int(args[1])
                except:
                    await ctx.send('Invalid arguments lol')
                    return
                if not new_cost > COST_EVERYONE:
                    await ctx.send('you are *not* decreasing the price, sorry')
                    return
                if not money_check(ctx.author, new_cost):
                    await ctx.send('you need to be able to afford the new price')
                    return
                dm.add_money(ctx.author.id, -1*new_cost)
                COST_EVERYONE = new_cost
                await ctx.send('An opressor has risen to deny the commonfolk their rights (price succesfully changed)')
            case 'ookie':
                if not money_check(ctx.author, COST_COOKIE):
                    await ctx.send('cashless behaviour')
                    return
                dm.add_money(ctx.author.id, -1*COST_COOKIE)
                await ctx.send(f'<@{me}> cookie has been redeemed')
            case _:
                await ctx.send('nah')
                return

#TODO this
@client.command(name='incidents')
@guild_restriction
async def incidents(ctx, *args):
    pass

@client.command(name='clear')
@guild_restriction
async def clear(ctx, *args):
    dm.clear_punishment(ctx.author.id)

# List statistics
@client.command(name='stats')
@guild_restriction
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
    if arg == 'server':
        response = format_stats(ctx.guild)
        await ctx.send(response)
        return
    elif arg in ['mean', 'count', 'median', 'max', 'min', 'last', 'balance']:
        stat = arg
        res = dm.stats(ctx.author.id, [member.id for member in ctx.guild.members], stat)
        if stat == 'count':
            res = [(ctx.guild.get_member(user_id).name, str(count)) for user_id, count in res[:10]]
            longest_name = max([len(name) for name,time in res])
        if stat == 'balance':
            res = [(ctx.guild.get_member(user_id).name, str(money)) for user_id, money in res[:10]]
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
            case 'balance': response = 'Who has the most bisches (and cash):' + response
        await ctx.send(response)
        return
    else:   
        print(arg)
        await ctx.send('thats not a real statistic ._. \n check your own stats for options')
        return

# allows you to place bets on who will be the next to fail an int check
@client.command(name='bet')
@guild_restriction
async def bet(ctx, *args):
    if len(args) == 0:
        bt = dm.get_bet(ctx.author.id)
        response = f'Your bet: {"None" if bt[0]==0 else client.get_guild(client.active_guild).get_member(bt[0]).name} {bt[1]}\n'
        response = str(dm.bets)
        for user_id in dm.bets.get_dumbass_candidates():
            user_id =int(user_id)
            str_id = str(user_id)
            username = f'{client.get_guild(client.active_guild).get_member(user_id).name:<{len(str_id)}}'
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
@client.command(name='rollies')
@guild_restriction
async def rollies(ctx: discord.ext.commands.Context):
    today_midnight = (datetime.datetime.now(datetime.timezone.utc)+AMS_OFFSET).replace(hour=0,minute=0,second=0,microsecond=0)
    lastd = dm.get_last_daily(ctx.author.id)+AMS_OFFSET
    now = ctx.message.created_at+AMS_OFFSET
    
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
    match result:
        case 1:
            await punish(ctx.author.id, ctx.channel, reason='ha ha')
        case 15:
            pass
        case 69:
            await ctx.send('nice')
        case 420:
            await ctx.send('nice')
        case 1000:
            sleep(1.8)
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



@client.command(name='steal')
@guild_restriction
async def steal(ctx: commands.Context, *args):
    dex, pouch = dm.get_steal_stats(ctx.author.id)
    if len(args) == 0:
        response = f'''
DEX:   +{dex}
POUCH: +{pouch}%

Your success is calculated using:
d100 + DEX({dex}) - PROT(1 per 10000 of victim wealth)
```
1       | crit fail     | immedate guards
2 - 50  | fail          | gain nothing
51 - 90 | success       | 2(+{pouch})% of victim's wealth
91 - 99 | great success | 4(+{pouch})% of victim's wealth
100     | crit success  | 8(+{pouch})% of victim's wealth
```
rolling a 1 or 100 are always crit fail or success
'''
        await ctx.send(response)
    elif len(args) == 1:
        victim = ctx.guild.get_member_named(str(args[0]))
        if victim == None:
            await ctx.send('No user with that name')
            return
        redeemable, tim = can_redeem(ctx.author, 'steal', COOLDOWN_STEAL)
        if not redeemable:
            now = datetime.datetime.now(datetime.timezone.utc)
            delta_time = (tim + COOLDOWN_STEAL) - now
            await ctx.send(f'Only 1 theft per 6 hrs sorrgy (cd: {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s))')
            return
        victim_wealth = dm.get_money(victim.id)
        roll = random.randint(1,100)
        result = roll + dex - victim_wealth//10000
        response = f'''
{roll} + DEX({dex}) - PROT({victim_wealth//10000}) = {result}\n
'''
        #this is horribly implemented but i don't care
        if roll == 1 or result <= 1:
            await ctx.send(response + "uh oh...")
            await punish(ctx.author.id, ctx.channel, reason="Generational fumble")
            return
        elif roll == 100 or result >= 100:
            stolen = round(victim_wealth*((8+pouch)/100))
            dm.add_money(ctx.author.id, stolen)
            dm.add_money(victim.id, -1*stolen)
            await ctx.send(response + f"Critical success!!\nStolen: {stolen} (New balance: {dm.get_money(ctx.author.id)})")
        elif result >= 91:
            stolen = round(victim_wealth*((4+pouch)/100))
            dm.add_money(ctx.author.id, stolen)
            dm.add_money(victim.id, -1*stolen)
            await ctx.send(response + f"Great success!\nStolen: {stolen} (New balance: {dm.get_money(ctx.author.id)})")
        elif result >= 51:
            stolen = round(victim_wealth*((2+pouch)/100))
            dm.add_money(ctx.author.id, stolen)
            dm.add_money(victim.id, -1*stolen)
            await ctx.send(response + f"Success\nStolen: {stolen} (New balance: {dm.get_money(ctx.author.id)})")
        else:
            stolen = 0
            await ctx.send(response + "Mission failed, we'll get 'em next time")
        dm.add_steal_attempt(ctx.author.id, victim.id, datetime.datetime.now(datetime.timezone.utc), stolen)
        dm.shop[(ctx.author.id,'steal')] = datetime.datetime.now(datetime.timezone.utc)
    else:
        await ctx.send('Invalid arguments lol')
        return

@client.command(name='guards')
@guild_restriction
async def guards(ctx: commands.Context, *args):
    steals = dm.get_all_steals(ctx.author.id)
    happens = False
    recovered = 0
    if not steals == None:
        for perp_id in steals.keys():
            time, amount = steals[perp_id]
            now = datetime.datetime.now(datetime.timezone.utc)
            if time + TIME_PERFECT_GUARDS + TIME_IMPERFECT_GUARD > now:
                if not happens:
                    await ctx.send("STOP! You violated the law >:(")
                timedelta = time + TIME_PERFECT_GUARDS - now
                timedelta = timedelta.total_seconds()
                await punish(perp_id, ctx.channel, reason="Zwieber, niet stelen!")
                if timedelta > 0:
                    await ctx.send("Perfect Parry!!")
                    recovered += amount
                else:
                    mult = 1 + (timedelta / TIME_IMPERFECT_GUARD.total_seconds())
                    recovered += max(round(amount*mult),1)
                happens = True
        dm.clear_steals(ctx.author.id)
    if not happens:
        await ctx.send('We couldnt find anything sire...')
    else:
        dm.add_money(ctx.author.id, recovered)
        dm.add_money(perp_id, -1*recovered)
        await ctx.send(f'Recovered: {recovered}')


@client.command(name='charity')
@guild_restriction
async def charity(ctx: commands.Context, *args):
    if len(args) == 2:
        try:
            if ctx.message.raw_mentions:
                user_id = ctx.message.raw_mentions[0]
            else:
                user = ctx.guild.get_member_named(str(args[0]))
                if user == None:
                    await ctx.send('No user with that name')
                    return 
                user_id = user.id
            charity_amount = int(args[1])
        except:
            await ctx.send('Invalid arguments lol')
            return
        if charity_amount < 0:
            await ctx.send('not today satan')
            return
        if dm.get_money(ctx.author.id) + dm.get_bet(ctx.author.id)[1] < charity_amount:
            await ctx.send(f'cant give what you dont have :pensive:\n(Your balance is: {dm.get_money(ctx.author.id)})')
            return
        dm.add_money(ctx.author.id, -1*charity_amount)
        dm.add_money(user_id, charity_amount)
        await ctx.send(f'Money transfered\n(New balance: {dm.get_money(ctx.author.id)})')
        return
    
    else:
        await ctx.send('Invalid arguments lol')
        return

@client.command(name='kys')
@guild_restriction
async def kys(ctx: commands.Context, *args):
    redeemable, tim = can_redeem(ctx.author, 'kys', COOLDOWN_KYS)
    if not redeemable:
        now = datetime.datetime.now(datetime.timezone.utc)
        delta_time = (tim + COOLDOWN_KYS) - now
        await ctx.send(f'"Dont be a sour loser lmao"\n- Confusionus or smth\n*(cooldown: {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s))*')
        return
    if not ctx.message.mentions:
        await ctx.send("Tag someone, idiot")
        return
    mention = ctx.message.mentions[0]
    victim = random.choice([mention, ctx.author])
    await punish(victim.id, ctx.channel, reason="krill yourshelf")
    dm.shop[(victim.id,'kys')] = datetime.datetime.now(datetime.timezone.utc)

# @guild_restriction
# @client.command
# async def clown(ctx, *args):
    # if len(args) > 1:
        # await ctx.send("Invalid arguments lol")
        # return
    # compression = 0
    # if len(args) == 1:
        # if type(args[0]) == int:
            # compression = args[0]
            # if compression < 0:
                # await ctx.send("# YOU SHALL NOT *UN*-COMPRESS THE CLOWN")
                # return
        # elif args[0] == "origin":
            # original = True
            ## display original clown           
        # else:
            # await ctx.send("Invalid arguments lol")
            # return
    # if money_check(author_id, compression):
        # dm.add_money(author_id, compression*-1)
        # compress_clown()
    # else:
        # ctx.send("Imagine being too poor to compress clowns.\nWouldn't wanna to be you mate")

# @client.command()
# async def woke_trivia(ctx):

# @client.command()
# async def wild_magic(ctx):

# @client.command()
# async def scp():  

# Run the client
if __name__ == "__main__":
    if TEST_MODE:
        client.run(TOKEN)
    else:
        client.run(TOKEN, log_handler=handler, log_level=logging.INFO)




