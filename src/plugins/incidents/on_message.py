from discord import Message
import random

from src.pluginbot import sig_on_message
from src.utils import format_timedelta
from src.signal import Signal

from .incident_schema import Incident
from .interface_settings import sticker_check
from .interface_db import read_last_guild_incident

INSULTS = ['Idiot', 'Dumbass', 'Stupid', 'Unintelligent', 'Fool', 'Moron', 'Dummy', 'Daft', 'Unwise', 'Half-baked',
            'Knobhead', 'Hingedly-impaired', 'Architectually challenged', 'Ill-advised', 'Imbecile', 'Dim', 'Unthinking',
            'Half-witted', 'Low intelligence specimen'] # particularly fond of Architectually challenged

sig_on_incident = Signal("incident")

@sig_on_message.connect
async def incident_handler(message: Message):
    if not message.stickers: return
    if not await sticker_check(message.guild.id, message.stickers[0].id): return

    last_incident = await get_last_guild_incident([dumbass.id for dumbass in message.guild.members])
    current_incident = Incident(message.author.id, message.created_at)
    await current_incident.save()

    if last_incident:
        interval = current_incident - last_incident
        response = random.choice(INSULTS) + '\nYou ruined a ' + format_timedelta(interval.length) + ' long collective streak >:('
    else:
        response = random.choice(INSULTS) + '\nCongrats! You are the first dumbass of the guild'
    await message.reply(response)
    await sig_on_incident.emit(message)


async def get_last_guild_incident(dumbass_ids: list[int]) -> Incident:
    rows = await read_last_guild_incident(dumbass_ids)
    if not rows: return None
    else: return Incident.parser(rows[0])

