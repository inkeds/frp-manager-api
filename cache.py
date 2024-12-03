from functools import wraps
from typing import Any, Callable
import time
from collections import OrderedDict
from logger import setup_logger

logger = setup_logger("cache")

class LRUCache:
    def __init__(self, maxsize: int = 100, ttl: int = 300):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}

    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key in self.cache:
            # 检查是否过期
            if time.time() - self.timestamps[key] > self.ttl:
                self.cache.pop(key)
                self.timestamps.pop(key)
                return None
            # 更新访问顺序
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.maxsize:
                # 移除最久未使用的项
                oldest = next(iter(self.cache))
                self.cache.pop(oldest)
                self.timestamps.pop(oldest)
        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self) -> None:
        """清除所有缓存"""
        self.cache.clear()
        self.timestamps.clear()

# 创建全局缓存实例
cache = LRUCache()

def cached(ttl: int = 300):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            cache.set(cache_key, result)
            logger.debug(f"Cache miss for {cache_key}, cached new result")
            return result
        return wrapper
    return decorator
