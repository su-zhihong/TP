"""
缓存服务层。
实现防击穿、防穿透、防雪崩等 Redis 高级用法。
"""
import json
from typing import Optional, Callable, Awaitable, Any
from backend.core.redis_client import redis_client
from backend.utils.lock import distributed_lock
from backend.utils.bloom_filter import food_bloom


async def get_food_with_fallback(
    food_name: str,
    fetch_func: Callable[[], Awaitable[Optional[dict]]],
    cache_key_prefix: str = "food_detail",
    min_ttl: int = 300,
    max_ttl: int = 600
) -> Optional[dict]:
    """
    获取食物详情，带多层缓存保护策略：
    
    1. 布隆过滤器防穿透：检查食物名称是否存在于布隆过滤器，
       如果不存在直接返回 None，避免穿透到 Neo4j。
    
    2. Redis 缓存查询：先查缓存，命中直接返回（快速响应）。
    
    3. 分布式锁防击穿：缓存过期时，使用 SET NX EX 获取锁，
       只有获得锁的线程才能查询 Neo4j 并重建缓存，
       其他线程等待后读取新缓存。
    
    4. 随机 TTL 防雪崩：设置缓存时附加随机 TTL（300-600秒），
       防止大量缓存同时过期导致数据库压力暴增。
    """
    # ---- 第一步：布隆过滤器检查，防穿透 ----
    # 此处使用布隆过滤器拦截不存在食物，避免穿透到 Neo4j
    if not food_bloom.exists(food_name):
        return None

    cache_key = f"{cache_key_prefix}:{food_name}"
    
    # ---- 第二步：查询缓存 ----
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    # ---- 第三步：分布式锁，防击穿 ----
    lock_key = f"lock:{cache_key}"
    async with distributed_lock(lock_key, expire=10) as acquired:
        if acquired:
            # 获得锁，查询数据库重建缓存
            data = await fetch_func()
            if data:
                # 随机 TTL 防雪崩
                await redis_client.set_with_random_ttl(cache_key, json.dumps(data, ensure_ascii=False), min_ttl, max_ttl)
            return data
        else:
            # 未获得锁，等待后尝试从缓存读取
            import asyncio
            await asyncio.sleep(0.1)
            cached = await redis_client.get(cache_key)
            if cached is not None:
                return json.loads(cached)
            return None


async def get_cached_or_fetch(
    cache_key: str,
    fetch_func: Callable[[], Awaitable[Any]],
    ttl: int = 300,
    use_random_ttl: bool = False,
    min_ttl: int = 300,
    max_ttl: int = 600
) -> Any:
    """
    通用缓存查询：先查缓存，未命中则调用 fetch_func 获取并缓存。
    可选择是否使用随机 TTL。
    """
    cached = await redis_client.get(cache_key)
    if cached is not None:
        return json.loads(cached)
    
    data = await fetch_func()
    if data is not None:
        if use_random_ttl:
            await redis_client.set_with_random_ttl(cache_key, json.dumps(data, ensure_ascii=False), min_ttl, max_ttl)
        else:
            await redis_client.set(cache_key, json.dumps(data, ensure_ascii=False), ex=ttl)
    return data


async def invalidate_cache(pattern: str):
    """
    按模式清除缓存。
    注意：生产环境应使用 Redis SCAN 命令分批次删除。
    """
    # 简单的单key删除，实际可使用 SCAN + DEL
    await redis_client.delete(pattern)