from typing import Coroutine
import inspect
import logging

logger = logging.getLogger(__name__)

class Signal:

    def __init__(self, name: str):
        self.name = name
        self._subscribers: list[Coroutine] = []
    
    def connect(self, func):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("functions connected to signals must be async")
        logger.debug(f"Connecting function {func.__name__} to signal {self.name}...")
        self._subscribers.append(func)

    async def emit(self, *args, **kwargs):
        for func in self._subscribers:
            logger.debug(f"Emitting signal {self.name} to function: {func.__name__}...")
            await func(*args, **kwargs)