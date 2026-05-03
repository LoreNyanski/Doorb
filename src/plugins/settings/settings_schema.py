from typing import Generic, TypeVar, Callable

T = TypeVar("T")

settings_registry: dict[str, Setting] = {}

def register_setting(setting: Setting):
    settings_registry[setting.key] = setting

class Setting(Generic[T]):
    def __init__(
        self,
        key: str,
        default: T,
        parser: Callable[[str], T],
        serializer: Callable[[T], str],
        description: str = ""
    ):
        self.key = key
        self.default = default
        self.parser = parser
        self.serializer = serializer
        self.description = description