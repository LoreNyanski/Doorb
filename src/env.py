import os
from dotenv import load_dotenv

TEST_MODE = os.getenv("TEST_MODE", "True") == "True"

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")

TEST_GUILD_ID = int(os.getenv("TEST_GUILD_ID"))

lore = os.getenv("lore")
shibe = os.getenv("shibe")