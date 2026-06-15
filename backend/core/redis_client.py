"""
Redis 客户端封装。
包含：连接池、布隆过滤器（内存模拟 + RedisBloom 预留）、限流器封装。
此处使用布隆过滤器拦截不存在食物，避免穿透到 Neo4j。
"""
import random
import redis.asyncio as redis
from typing import Optional
from backend.core.config import settings


class RedisClient:
    """Redis 异步客户端封装"""

    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None

    async def initialize(self):
        """初始化连接池"""
        self._pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD or None,
            decode_responses=True,
            max_connections=50,
            protocol=2,  # 使用 RESP2 协议，兼容低版本 Redis
        )
        self._client = redis.Redis(connection_pool=self._pool)

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            raise RuntimeError("Redis client not initialized. Call `initialize()` first.")
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            await self._pool.disconnect()

    # ---- 缓存操作 ----

    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """设置缓存，支持过期时间"""
        await self.client.set(key, value, ex=ex)

    async def set_with_random_ttl(self, key: str, value: str, min_ttl: int = 300, max_ttl: int = 600):
        """
        设置缓存并附加随机 TTL，防止大量缓存同时过期导致缓存雪崩。
        """
        ttl = random.randint(min_ttl, max_ttl)
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        """删除缓存"""
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """判断 key 是否存在"""
        return await self.client.exists(key) > 0

    # ---- 分布式锁 ----

    async def acquire_lock(self, lock_key: str, lock_value: str, expire: int = 10) -> bool:
        """
        使用 SET NX EX 实现分布式锁，防止缓存击穿。
        只有获得锁的线程才能重建缓存。
        """
        # SET NX EX: 当 key 不存在时设置，并设置过期时间
        result = await self.client.set(lock_key, lock_value, nx=True, ex=expire)
        return result is True

    async def release_lock(self, lock_key: str, lock_value: str):
        """
        释放分布式锁（校验 value 防止误删）。
        生产环境建议使用 Lua 脚本确保原子性。
        """
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.client.eval(lua_script, 1, lock_key, lock_value)

    # ---- 原子计数 ----

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        使用 INCR 实现原子计数器，记录每个食物查询次数。
        """
        return await self.client.incr(key, amount)

    async def get_counter(self, key: str) -> int:
        """获取计数器值"""
        val = await self.client.get(key)
        return int(val) if val else 0

    # ---- 有序集合（排行榜） ----

    async def zincrby(self, key: str, amount: int, member: str):
        """有序集合原子递增"""
        await self.client.zincrby(key, amount, member)

    async def zrevrange(self, key: str, start: int = 0, end: int = 9, withscores: bool = True) -> list:
        """获取有序集合排名（从高到低）"""
        return await self.client.zrevrange(key, start, end, withscores=True)

    # ---- 限流（Lua 脚本） ----

    async def allow_request(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """
        滑动窗口限流，使用 Lua 脚本保证原子性。
        每 IP 每分钟 N 次请求限制。
        """
        lua_script = """
        local key = KEYS[1]
        local max = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = redis.call('TIME')[1]
        
        -- 移除窗口外的记录
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        
        -- 统计当前窗口请求数
        local count = redis.call('ZCARD', key)
        
        if count < max then
            -- 添加当前请求
            redis.call('ZADD', key, now, now .. ':' .. math.random())
            redis.call('EXPIRE', key, window)
            return 1
        else
            return 0
        end
        """
        result = await self.client.eval(lua_script, 1, key, max_requests, window_seconds)
        return result == 1

    # ---- 布隆过滤器（内存版模拟，生产环境使用 RedisBloom）----
    # 生产环境应使用 RedisBloom 模块的 BF.ADD / BF.EXISTS 命令
    # 这里使用 pybloom_live 的内存实现，说明原理

    def _get_bloom_key(self, name: str) -> str:
        return f"bloom_filter:{name}"

    async def bloom_add(self, filter_name: str, item: str):
        """
        向布隆过滤器添加元素。
        生产环境使用 RedisBloom: BF.ADD <filter_name> <item>
        """
        # 使用 Redis set 模拟（非真正的 Bloom Filter，仅供演示架构）
        # 生产环境应使用 RedisBloom
        key = self._get_bloom_key(filter_name)
        await self.client.sadd(key, item)

    async def bloom_exists(self, filter_name: str, item: str) -> bool:
        """
        检查布隆过滤器中是否存在某元素。
        此处使用布隆过滤器拦截不存在食物，避免穿透到 Neo4j。
        生产环境使用 RedisBloom: BF.EXISTS <filter_name> <item>
        """
        key = self._get_bloom_key(filter_name)
        return await self.client.sismember(key, item)


# 全局单例
redis_client = RedisClient()