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
CHANCE_AMOGUS = 10
CHANCE_DAD = 10
CHANCE_HIVEMIND = 2
REQUIREMENT_HIVEMIND = 3

# Globals
last_message = ''
client.active_sticker = 1305957931304615997

# -----------------------------------------------------------------------------------------
#                                    Functions
# -----------------------------------------------------------------------------------------


# Given an int 'chance' returns true with 1/chance probability 
def rndm(chance) -> bool:
    if chance < 1: return False
    return random.randint(1,chance) == 1
    

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

# Message handler
@client.event
async def on_message(message):
    global last_message

    # Dont respond to your own shit idiot
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


# -----------------------------------------------------------------------------------------
#                                    Meta commands
# -----------------------------------------------------------------------------------------

# Test command
@client.command(name='hi')
async def hi(ctx):
    await ctx.send('haiii :3')

# Display list of commands
@client.command()
async def help(ctx):
    response = '''
Welcome to doorbot!

I am here to tell you who's the biggest dumbass on your discord server.
To set up which sticker I should be tracking please use the 'sticker' command

List of commands:
- General:
    - help - youre reading it rn idiot

- Door related:
    - stats [optional: user id] - displays the statistics of user. If no id provided the default is you.
    - serverstats [optional: statistic name] - displays the best member in each statistic. If specific stat provided as argument, displays the that specific statistic for all members.
    - bet [user] [amount] - place a bet on who will be the next dumbass.

- Games:
    - daily - gamba
    - blackjack - gamba2: electric boogaloo
    - woke_trivia - Can you guess the videogame based on how the steam curator 'Woke Content Detector' reviewed it?
    - wild_magic
    - scp
    '''
    
    await ctx.send(response)

# -----------------------------------------------------------------------------------------
#                                   Door shenanigans
# -----------------------------------------------------------------------------------------

# List statistics for yourself
@client.command()
async def stats(ctx):
    response = '''
You fool, you buffoon, you thought I already implemented this?? 
    - Lore
'''
    await ctx.send(response)

# list of all statistics with the person in #1 of said stat
# if specific stat given as arg - lists that stat with all server ppl
async def serverstats(ctx):
    response = '''
You fool, you buffoon, you thought I already implemented this?? 
    - Lore
'''
    await ctx.send(response)

# allows you to place bets on who will be the next to fail an int check
async def bet(ctx):
    response = '''
You fool, you buffoon, you thought I already implemented this?? 
    - Lore
'''
    await ctx.send(response)

# -----------------------------------------------------------------------------------------
#                                        Misc
# -----------------------------------------------------------------------------------------

# just straight up blackjack
async def blackjack(ctx):
    response = '''
You fool, you buffoon, you thought I already implemented this?? 
    - Lore
'''
    await ctx.send(response)

# daily roll between 1 and 1000 - make it look like the google rng - 
@client.command()
async def rollies(ctx):
    delta_time = dm.get_delta_daily(ctx.author.id)
    if delta_time.days > 1:
        result = random.randint(1, 1000)
        dm.daily(ctx.author.id, result)
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
    if result == 1000:
        await ctx.send(response)
        await ctx.send('HOLY SHIIIT')
        await ctx.send(f'<@{shibe}>')
        await ctx.send(f'IT FINALLY HAPPENED <@{shibe}>')
        await ctx.send(f'<@{shibe}>')
        return
    else:
        delta_time = datetime.timedelta(days=1) - delta_time
        response = f'''
Bisch wait {delta_time.seconds//3600} hour(s) {(delta_time.seconds%3600)//60} minute(s) before your next roll
        '''
    await ctx.send(response)

@client.command
async def woke_trivia(ctx):
    response = '''
You fool, you buffoon, you thought I already implemented this?? 
    - Lore
'''
    await ctx.send(response)




# Run the client
if __name__ == "__main__":
    client.run(TOKEN, log_handler=handler)