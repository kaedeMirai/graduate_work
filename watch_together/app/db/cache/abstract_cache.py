from abc import ABC, abstractmethod
from datetime import timedelta


class AbstractCacheStorage(ABC):

    @abstractmethod
    async def get(self, key: str, **kwargs): ...

    @abstractmethod
    async def set(self, key: str, data: str, exp: timedelta | int, **kwargs): ...

    @abstractmethod
    async def hset(self, key: str, name: str, data: str): ...

    @abstractmethod
    async def rpush(self, key: str, data: str): ...

    @abstractmethod
    async def lrange(self, key: str, start: int, stop: int): ...

    @abstractmethod
    async def hvals(self, key: str): ...
