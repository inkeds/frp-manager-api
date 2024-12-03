from typing import Any, Optional
import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        self.default_ttl = 3600  # 1小时默认过期时间

    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        return await self.redis_client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        return await self.redis_client.set(
            key,
            value,
            ex=ttl or self.default_ttl
        )

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        return await self.redis_client.delete(key) > 0

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return await self.redis_client.exists(key) > 0

    async def increment(self, key: str) -> int:
        """增加计数器"""
        return await self.redis_client.incr(key)

    async def decrement(self, key: str) -> int:
        """减少计数器"""
        return await self.redis_client.decr(key)

    async def set_many(
        self,
        mapping: dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """批量设置缓存值"""
        pipeline = self.redis_client.pipeline()
        for key, value in mapping.items():
            pipeline.set(key, value, ex=ttl or self.default_ttl)
        results = await pipeline.execute()
        return all(results)

    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """批量获取缓存值"""
        pipeline = self.redis_client.pipeline()
        for key in keys:
            pipeline.get(key)
        values = await pipeline.execute()
        return dict(zip(keys, values))

    async def delete_many(self, keys: list[str]) -> int:
        """批量删除缓存值"""
        return await self.redis_client.delete(*keys)

    async def clear_prefix(self, prefix: str) -> int:
        """清除指定前缀的所有缓存"""
        keys = await self.redis_client.keys(f"{prefix}:*")
        if keys:
            return await self.redis_client.delete(*keys)
        return 0

cache_service = CacheService()
