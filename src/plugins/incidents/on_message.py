from discord import Message
import random

from src.pluginbot import on_message_handler
from src.utils import format_timedelta

from .incident_schema import Incident
from .interface_settings import sticker_check
from .interface_db import read_last_guild_incident

INSULTS = ['Idiot', 'Dumbass', 'Stupid', 'Unintelligent', 'Fool', 'Moron', 'Dummy', 'Daft', 'Unwise', 'Half-baked',
            'Knobhead', 'Hingedly-impaired', 'Architectually challenged', 'Ill-advised', 'Imbecile', 'Dim', 'Unthinking',
            'Half-witted', 'Low intelligence specimen'] # particularly fond of Architectually challenged

@on_message_handler()
async def incident_handler(message: Message):
    if not message.stickers: return
    if not await sticker_check(message.guild.id, message.stickers[0].id): return

    last_incident = await get_last_guild_incident([dumbass.id for dumbass in message.guild.members])
    current_incident = Incident(message.author.id, message.created_at)
    current_incident.save()
    interval = current_incident - last_incident

    response = random.choice(INSULTS) + '\nYou ruined a ' + format_timedelta(interval.length) + ' long streak >:('
    await message.reply(response)

async def get_last_guild_incident(dumbass_ids: list[int]) -> Incident:
    rows = await read_last_guild_incident(dumbass_ids)
    if not rows: return None
    else: return Incident.parser(rows[0])

