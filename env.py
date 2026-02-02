import os
from dotenv import load_dotenv


TEST_MODE = False


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")

shibe = int(os.getenv("shibe"))
lore = int(os.getenv("lore"))

guild = int(os.getenv("test_guild")) if TEST_MODE else int(os.getenv("main_guild"))
sticker = int(os.getenv("test_sticker")) if TEST_MODE else int(os.getenv("tracked_sticker"))