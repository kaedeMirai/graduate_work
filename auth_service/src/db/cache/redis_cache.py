from redis.asyncio import Redis
from datetime import timedelta

from db.cache.abstract_cache import AbstractCacheStorage

cache_client: Redis | None


class RedisCacheStorage(AbstractCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, **kwargs):
        return await self.redis.get(key)

    async def set(self, key: str, data: str, exp: timedelta | int, **kwargs):
        await self.redis.set(key, data, exp)


async def get_cache() -> AbstractCacheStorage | None:
    return RedisCacheStorage(cache_client)
