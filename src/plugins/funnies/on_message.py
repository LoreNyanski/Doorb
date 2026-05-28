from discord import Message
import asyncio
import re
from PIL import Image as Im
from io import BytesIO
from discord import File

from src.pluginbot import sig_on_message
from src.utils import frg_check

from .predicates import dad_check, fucking_check, salute_check, amogus_check, hivemind_check, s67_check, nry_check

@sig_on_message.connect
async def process_funnies(message: Message):
    if amogus_check(message.content):
        msg = message.content.replace('||','')
        response = '||'
        for i in 'amogus':
            indx = msg.lower().find(i)
            response += msg[:indx]
            response += '||' + msg[indx] + '||'
            msg = msg[indx+1:]
        response += msg + '||'

        await message.reply(content=response.replace('||||',''))

    elif s67_check(message.content):
        interval = 0.01
        amount = 6
        left_hands = """
haha, 67
🫴
      🫴
        """
        middle_hands ="""
haha, 67
🫴🫴
"""
        right_hands = """
haha, 67
      🫴
🫴
"""
        async def hands():
            hands_message = await message.reply(left_hands)
            is_left = True
            for i in range(amount):
                await asyncio.sleep(interval)
                is_left = not is_left
                try:
                    await hands_message.edit(content=middle_hands)
                    await asyncio.sleep(interval/2)
                    await hands_message.edit(content=left_hands if is_left else right_hands)
                except:
                    break

        asyncio.create_task(hands())

    elif dad_check(message.content):
        pattern = re.compile(r"^I('| a)?m ", re.IGNORECASE)
        msg = message.content
        response = 'Hi '
        response += re.sub(pattern, '', msg).strip()
        response += ", I'm dad :D"

        await message.reply(content=response)

    elif hivemind_check(message.content):
        response = message.content

        await message.channel.send(content=response)

    elif fucking_check(message.content):
        words = [i for i in message.content.split() if i != '']
        fuking = [i for i, word in enumerate(words) if re.match(r"fucking?", word, re.IGNORECASE)][0]
        response = words[fuking - 1] + " is doing WHAT to " + words[fuking + 1] + " now???"

        await message.reply(content=response)

    elif salute_check(message.content):
        await message.add_reaction('🫡')

    elif nry_check(message):
        if not frg_check(message.guild.id): return
        nry = Im.open('nry.png')
        with BytesIO() as im_buffer:
            await message.attachments[0].save(fp=im_buffer, seek_begin=True)

            with Im.open(fp=im_buffer) as im:
                
                nry_sized = nry.resize((nry.size[0]*im.size[1]//nry.size[1], im.size[1]))
                im.paste(nry_sized,(0,0),mask=nry_sized)

                output_buffer = BytesIO()
                im.save(output_buffer, format="PNG")
                output_buffer.seek(0)

        await message.reply(file=File(fp=output_buffer, filename="result.png"))
