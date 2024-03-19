from abc import ABC, abstractmethod
from datetime import timedelta


class AbstractCacheStorage(ABC):
    @abstractmethod
    async def get(self, key: str, **kwargs):
        pass

    @abstractmethod
    async def set(self, key: str, data: str, exp: timedelta | int, **kwargs):
        pass
