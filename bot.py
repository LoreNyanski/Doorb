# VSCode terminal reminders lmao
# minimise terminal - ctrl + j
# interrupt terminal - ctrl + c

'''
<Message id=1319013025738522634 channel=<TextChannel id=1317049762330972190 name='bot-testing' position=1 nsfw=False news=False category_id=None> type=<MessageType.default: 0> author=<Member id=1311339750996705312 name='Door bot' global_name=None bot=True nick=None guild=<Guild id=543772806349848594 name='ayy' shard_id=0 chunked=True member_count=7>> flags=<MessageFlags value=0>>
'''

# bot.py
import os
import discord
import re
import random
import datetime

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# TODO: proper intents my guy
intents = discord.Intents.all()
client = discord.Client(intents=intents)



# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------



# CONSTANTS
CHANCE_AMOGUS = 1
CHANCE_DAD = 1
CHANCE_HIVEMIND = 1
REQUIREMENT_HIVEMIND = 3

# globals
last_msg = ''
last_msg_time = datetime.datetime.now()

# Given an int 'chance' returns true with 1/chance probability 
def rndm(chance) -> bool:
    if chance < 1: return False
    return random.randint(1,chance) == 1

# better version of hivemind. Shouldn't just check the last 3 messages but if the same message was said
# 3 times in the past idk 10 seconds. Also doesnt send the message if it has already done so
def hivemind_check(message, lst) -> bool:
    global last_msg
    if len(lst) == 0 or last_msg == message.content: return False
    first = message.content
    return all(first==i.content for i in lst) and rndm(CHANCE_HIVEMIND)

def amogus_check(message) -> bool:
    return re.search(r'.*a.*m.*o.*g.*u.*s.*', message.content, re.IGNORECASE) and not re.search(r'.*amogus.*', message.content, re.IGNORECASE) and rndm(CHANCE_AMOGUS)

def dad_check(message) -> bool:
    return re.search(r"^I('| a)?m ", message.content, re.IGNORECASE) and rndm(CHANCE_DAD)



# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------



@client.event
async def on_ready():
    print(f'{client.user} has logged in\n\nConnected to the following guilds:')
    for guild in client.guilds:
        print(f'    {guild.name} (id: {guild.id})')

@client.event
async def on_message(message):
    global last_msg, last_msg_time

    if message.author == client.user:
        print(message)
        last_msg = message.content
        last_msg_time = datetime.datetime.now()
        return

    # test run
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
        return

    # Dad bot feature
    if dad_check(message):
        pattern = re.compile(r"^I('| a)?m ", re.IGNORECASE)
        msg = message.content
        response = 'Hi '
        response += re.sub(pattern, '', msg).strip()
        response += ", I'm dad :D"

        await message.channel.send(content=response, reference=message.to_reference())
        return

    # Hivemind
    if hivemind_check(message, [msgs async for msgs in message.channel.history(limit=REQUIREMENT_HIVEMIND)]):
        msg = message.content
        response = msg

        await message.channel.send(content=response)
        return

client.run(TOKEN)