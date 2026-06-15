"""
分布式锁辅助函数。
"""
import uuid
from contextlib import asynccontextmanager
from backend.core.redis_client import redis_client


@asynccontextmanager
async def distributed_lock(lock_key: str, expire: int = 10):
    """
    分布式锁上下文管理器。
    使用 SET NX EX 实现，自动释放锁。
    
    使用场景：热点食物缓存过期时，防止多个线程同时查询数据库重建缓存。
    """
    lock_value = str(uuid.uuid4())
    acquired = await redis_client.acquire_lock(lock_key, lock_value, expire)
    try:
        yield acquired
    finally:
        if acquired:
            await redis_client.release_lock(lock_key, lock_value)