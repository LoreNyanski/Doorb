# bot.py
import os
import discord
import re

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
client = discord.Client(intents=intents)

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


    # Amongus detector
    if re.search('.*a.*m.*o.*g.*u.*s.*', message.content):
        msg = message.content
        response = []
        for i in 'amogus':
            indx = msg.find(i)
            response.append(msg[:indx])
            response.append(msg[indx])
            msg = msg[min(indx+1,len(msg)):]
        response.append(msg)

        await message.channel.send('|| ' + '||'.join(response) + ' ||')

client.run(TOKEN)