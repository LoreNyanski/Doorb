from src.plugins.settings import Setting, register_setting, get_setting, Scope
from src.pluginbot import setup_handler

DEFAULT_STICKER = 1305957931304615997

@setup_handler()
async def setup_settings(client):
    sticker_setting = Setting(
        key="tracked_sticker",
        default=DEFAULT_STICKER,
        parser=lambda x: int(x),
        serializer=lambda x: str(x),
        description="The sticker a dumbass needs to send in case they want to report an incident"
        )
    register_setting(sticker_setting)

async def sticker_check(guild_id: int, sticker_id:int):
    return sticker_id == await get_setting(Scope.GUILD, guild_id, "tracked_sticker")
