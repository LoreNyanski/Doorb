# bot.py
import os
import discord
import re
import random

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# CONSTANTS
CHANCE_AMOGUS = 1
CHANCE_DAD = 1
CHANCE_HIVEMIND = 1
REQUIREMENT_HIVEMIND = 3

# TODO: proper intents my guy
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Given an int 'chance' returns true with 1/chance probability 
def rndm(chance):
    if chance < 1: return False
    return random.randint(1,chance) == 1

# Primitive version of hivemind
def all_same(lst):
    if len(lst) == 0: return True
    first = lst[0]
    return all(first==i for i in lst)

# better version of hivemind. Shouldn't just check the last 3 messages but if the same message was said
# 3 times in the past idk 10 seconds. Also doesnt send the message if it has already done so
def hivemind_check(lst):
    if client.user in [msgs.author for msgs in lst]: return False




@client.event
async def on_ready():
    print(f'{client.user} has logged in\n\nConnected to the following guilds:')
    for guild in client.guilds:
        print(f'    {guild.name} (id: {guild.id})')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # test run
    if message.content == 'door':
        await message.channel.send("look at this dumbass XD")


    # Amogus detector
    if re.search(r'.*a.*m.*o.*g.*u.*s.*', message.content, re.IGNORECASE) and rndm(CHANCE_AMOGUS):
        msg = message.content
        response = '||'
        for i in 'amogus':
            indx = msg.lower().find(i)
            response += msg[:indx]
            response += '||' + msg[indx] + '||'
            msg = msg[indx+1:]
        response += msg + '||'

        await message.channel.send(content=response.replace('||||',''), reference=message.to_reference())
        return

    # Dad bot feature
    if re.search(r"^I('| a)?m ", message.content, re.IGNORECASE) and rndm(CHANCE_DAD):
        pattern = re.compile(r"^I('| a)?m ", re.IGNORECASE)
        msg = message.content
        response = 'Hi '
        response += re.sub(pattern, '', msg).strip()
        response += ", I'm dad :D"

        await message.channel.send(content=response, reference=message.to_reference())
        return

    # Part of the hivemind - if same thing said in quick succession then repeat it aswell
    if all_same([msgs.content async for msgs in message.channel.history(limit=3)]) and rndm(CHANCE_HIVEMIND) == 1:
        msg = message.content
        response = msg

        await message.channel.send(content=response)
        return

client.run(TOKEN)