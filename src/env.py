import os
from dotenv import load_dotenv

TEST_MODE = os.getenv("TEST_MODE", "True") == "True"

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")

shibe = int(os.getenv("shibe"))
lore = int(os.getenv("lore"))

test_guild = int(os.getenv("test_guild"))
sticker = int(os.getenv("tracked_sticker"))