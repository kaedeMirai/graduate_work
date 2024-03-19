from redis.asyncio import Redis
from datetime import timedelta

from watch_together.app.db.cache.abstract_cache import AbstractCacheStorage


class RedisCacheStorage(AbstractCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, **kwargs):
        return await self.redis.get(key)

    async def set(self, key: str, data: str, exp: timedelta | int, **kwargs):
        data_bytes = data.encode("utf-8")
        await self.redis.set(key, data_bytes, exp)

    async def hset(self, key: str, name: str, data: str):
        await self.redis.hset(key, name, data)

    async def rpush(self, key: str, data: str):
        await self.redis.rpush(key, data)

    async def lrange(self, key: str, start: int, stop: int):
        return await self.redis.lrange(key, start, stop)

    async def hvals(self, key: str):
        return await self.redis.hvals(key)
