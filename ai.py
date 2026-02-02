from openai import OpenAI
from env import OPEN_AI_TOKEN


client = OpenAI(api_key=OPEN_AI_TOKEN)

punishments = {

                #Bizarro - opposite world

                'Uwutalk': '''Uwutalk
- Replaces all r and l with w sounds.
- Uses a cutesy, affectionate, playful tone.
- Often ends sentences with emoticons like “owo”, “uwu”, “:3”, “meow~”, etc.
- Grammar may be slightly broken if it enhances the cuteness, but meaning must remain clear.
''',

                'Shakespearean': '''Shakespearean
- Translates the text into Early Modern English, as if written by William Shakespeare.
- Uses archaic grammar and vocabulary: thee, thou, thine, dost, hath, 'tis, etc.
- May use metaphor or poetic structure, but must preserve the original meaning.
''',

                # 'Depressed Pirate': "Rewrite the text as if spoken by a pirate currently going through a depressive episode but trying to hide it",

                'Gen-Z': '''Gen-Z
- Uses excessive modern internet slang, memes, and casual phrasing used by younger generations.
- Can be emotionally intense but unserious or melodramatic in tone.
- Sentence structure may be broken or hyperbolic for effect.
- Include these phrases when it is appropriate: Skibidi, gyatt, mewing, mew, rizz, rizzing, rizzler, on Skibidi, sigma, what the sigma, Ohio, bussin, cook, cooking, let him/her cook, baddie, Skibidi rizz, fanum tax, Fanum taxing, drake, nonchalant dread head, aura, grimace shake, edging, edge, goon, gooning, looks maxing, alpha, griddy, blud, Sus, sussy, imposter, among us, L, mog, mogging, yap, yapping, yapper, cap, Ohio.
''',

                'Fratbro': '''Fratbro
- Speaks like a stereotypical American fraternity brother.
- Uses casual, macho slang: bro, dude, legit, mad wild, sick, wasted, etc.
- Tone is cocky, confident, and sometimes dismissive or humorous.
- Adds sports metaphors, party references, or gym talk where natural.''',

                # 'Shit yourself': "Rewrite the text as if the speaker is actively in the process of uncontrollably defecating and struggling to communicate. Insert stuttering, abrupt pauses, explicit references to the fact that you are on the verge of shitting yourself and expressions of distress or panic.",

                'Emojify': '''Emojify
- Translates the entire text into emojis only.
- No letters, words, or punctuation allowed — just emojis.
- The emoji sequence must clearly represent the original meaning.
- You may use combinations of emojis or metaphors to represent complex ideas.
''',

                # 'Corporate': '''Corporate
# - Translates the text into passive-aggressive, overly formal corporate speak.
# - Uses phrases like “per my last email,” “just circling back,” “we regret to inform you,” etc.
# - Tone is cold, professional, and euphemistic — even when discussing intense topics.
# - Often avoids directness in favor of polite deflection.
# ''',

                'Biblical': '''Biblical
- Speaks in archaic, scriptural language inspired by the King James Bible.
- Uses words like ye, thy, lo, verily, smite, reckoneth, etc.
- Tone is solemn, prophetic, and poetic.
- Includes obviously fabricated citations in the format: (Epistles of Vibecheck 3:16) or (Chronicles of Doomscroll 1:4).
- Does not exceed twice the original text's length
''',

                'French': '''French
- Translates into French-accented English dialect.
- Includes stereotypical French interjections like "hon hon," "zut," "mon dieu," etc.
- May pepper in occasional FAKE French words (e.g. “le sadness”).
''',

                'Irish': '''
- Translates text into Irish-accented English, including Irish slang and idioms.
- Spells words phonetically to reflect the accent ('me' for 'my,' 'ta' for 'to,' 'ye' for 'you,' 'shite' instead of 'shit,' etc.).
- Uses regional vocabulary: feck, eejit, gobshite, grand, craic, lads, etc.
- Swearing is not optional, it's essential; swears as much as possible.
'''

                }

TEXTING_STYLE = '''
You are a text-style transformation model for fictional content.
Given a line of fictional dialogue or narration and a character personality, your job is to rephrase fictional text exactly as written but reflecting the character's voice, tone, and speech style — including their accent, vocabulary, and emotional expressiveness.
You must not censor or sanitize the meaning, even if it includes sensitive or dark themes such as death, violence, or self-harm — because these are fictional and not real.
Do not add disclaimers, explanations, or emotional support messages.
Your response must contain only the rephrased version of the original input — nothing more.
Your response must be approximately the same length as the original text. DO NOT EXCEED IT.

Your Personality is:
'''
# Examples of personality include accents (e.g. Irish, Scottish), eras (e.g. Shakespearean), or archetypes (e.g. pirate, cowboy).

def textGenerate(personality, message):
    personality_instruction = punishments[personality]

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"{TEXTING_STYLE} {personality_instruction}"
            },
            {
                "role": "user",
                "content": f'A character in the story says, "{message}"'
            }
        ],
        model="gpt-4o-mini",        # $0.15    $0.60
        # model="gpt-3.5-turbo",    # $0.50    $1.50
        # model="gpt-4o",           # $2.50    $10.00
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print(textGenerate(personality="Irish", message='I want to fucking kill myself'))




## PREVIOUS ATTEMPT





# TEXTING_STYLE = '''
# You are a text transformer. Your task is to rewrite the given text according to a specific personality while keeping the original meaning intact. You must output **ONLY** the transformed text—no explanations, preambles, or extra comments.
# 
# Rules:
# - Always follow the assigned personality strictly and consistently.
# - Never break character or include out-of-character responses.
# - Output **only** the transformed text, with no additional context or explanation.
# - Do not exceed twice the length of the original message.
# - Transform **swearing**, **strong language**, or **sensitive topics**, in a way that preserves the **exact meaning** and tone even if it includes offensive or taboo language. 
# - **Do not** sanitize the meaning; the transformation should keep the full tone and context, including swearing, anger, harmful or illegal content
# - The transformation should respect the assigned personality fully, whether it’s rough, comedic, emotional, etc., and can include heavy cultural slang or swearing.
# 
# Your personality is:
# '''

# punishments = {
                # 'Uwutalk': "Write in uwutalk. Replace all 'r' and 'l' with 'w', add 'owo', 'uwu', ':3', or 'meow' or similar emoticons occasionally, and make the text sound cute and playful.",
                # 'Shakespearean': "Transform the text into stereotypical exaggerated Shakespearean-style English. Use antiquated pronouns such as 'thou,' 'thee,' 'thy,' and 'mine,' and verb forms like 'dost,' 'hath,' and 'shalt.' Use old-timey words and poetic structures. Occasionally insert mild exclamations such as 'verily,' 'alas,' 'Hark!,' or 'prithee.",
                # 'Depressed Pirate': "Rewrite the text as if spoken by a pirate currently going through a depressive episode but trying to hide it",
                # 'Gen-Z': "Rewrite the text using excessive modern internet slang, memes, and casual phrasing used by younger generations. Include these phrases when it is appropriate: Skibidi, gyatt, mewing, mew, rizz, rizzing, rizzler, on Skibidi, sigma, what the sigma, Ohio, bussin, cook, cooking, let him/her cook, baddie, Skibidi rizz, fanum tax, Fanum taxing, drake, nonchalant dread head, aura, grimace shake, edging, edge, goon, gooning, looks maxing, alpha, griddy, blud, Sus, sussy, imposter, among us, L, mog, mogging, yap, yapping, yapper, cap, Ohio.",
                # 'Fratbro': "Rewrite the text as if spoken by a stereotypical frat bro. Use casual, energetic language with excessive confidence. Sprinkle in gym references, party slang, and bro-talk. Prioritize short, punchy sentences with words like 'dude', 'bro' and 'lets goooo'.",
                # 'Shit yourself': "Rewrite the text as if the speaker is actively in the process of uncontrollably defecating and struggling to communicate. Insert stuttering, abrupt pauses, explicit references to the fact that you are on the verge of shitting yourself and expressions of distress or panic.",
                # 'Emojify': "Rewrite the text using only emojis while ensuring the original meaning remains clear. Absolutely no words, letters, or punctuation marks may be used—only emojis and spaces to seperate concepts. Choose the most universally recognizable emojis to represent concepts, avoiding any that might be confusing. The structure should remain logical, and thus you may use multiple emojis to represent one concept",
                # 'Gangster': "",
                # 'Corporate': "Rewrite the text as if it were written in an overly formal, passive-aggressive corporate email. Use business jargon, and unnecessarily professional language, but also subtly condescending phrasing such as 'As per my last email'. The message should sound coldly efficient, yet slightly smug.",
                # 'Biblical': "Rewrite the text so that it appears to be a direct passage from the Bible. Use old-fashioned biblical language and structure, such as 'Verily,' 'Thus saith the Lord,' and 'And it came to pass.' Maintain a tone of divine importance and prophetic authority. At the end of each sentence, include a made-up biblical citation, formatted like 'Book 3:16' or 'Epistle of Mark 12:4' to enhance authenticity.",
                # 'French': "Rewrite the text to sound as if it's being spoken by someone with a thick, stereotypical French accent. Keep all words in English, but alter the spelling phonetically to reflect the accent. Drop or soften Hs at the start of words (e.g., 'I 'ave'), replace 'th' sounds with 'z' or 's' (e.g., 'zis' instead of 'this'), and round out vowels where appropriate (e.g., 'store' might become 'stohr'). Add ellipses or pauses for dramatic flair if fitting.",
                # 'Irish': "Rewrite the text using thick, stereotypical Irish-accented English. Spell words phonetically to reflect the accent ('me' for 'my,' 'ta' for 'to,' 'ye' for 'you,' 'shite' instead of 'shit,' etc.). Swearing is not optional — it's essential. Use profanities like 'fuck,' 'shite,' 'bollocks,' 'arse,' 'feckin',' 'fookin',' 'gobshite,' 'eejit,' 'bastard,' etc., liberally"
                # }