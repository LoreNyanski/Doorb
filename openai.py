from openai import OpenAI
import os
import random

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
client = OpenAI(api_key=OPEN_AI_TOKEN)

TEXTING_STYLE = '''
You are a text transformer. Your task is to rewrite the given text according to a specific personality while keeping the original meaning intact. You must output **ONLY** the transformed text—no explanations, preambles, or extra comments.
Rules:
- Always follow the assigned personality strictly.
- Never add explanations or out-of-character responses.
- Output only the transformed text without any preamble.
- Try not to exceed twice the length of the original message.

Your personality is:
'''

# - The message must remain recognizable but should still sound as if it was spoken with that personality.
# '''

# PERSONALITY = random.choice(list(punishments.values()))

# MESSAGE = '''
# two steps ahead, i am always two steps ahead. this has been the greatest social experiment i’ve come to known, certainly the greatest social experiment of my current life. its alluring, its compelling, its gripping.
# '''
def textGenerate(personality, message):

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{TEXTING_STYLE}\n{personality}"
            },
            {
                "role": "user",
                "content": f"{message}"
            }
        ],
        model="gpt-4o-mini",        # $0.15    $0.60
        # model="gpt-3.5-turbo",    # $0.50    $1.50
        # model="gpt-4o",           # $2.50    $10.00
    )

    return response.choices[0].message.content