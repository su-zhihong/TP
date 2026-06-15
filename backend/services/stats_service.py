"""
统计服务。
使用 Redis 原子计数器记录食物查询次数，有序集合实现热门排行榜。
"""
from backend.core.redis_client import redis_client

# 食物查询次数计数器 key 前缀
FOOD_QUERY_COUNTER_PREFIX = "food_query_count"
# 热门食物排行榜 key
HOT_FOODS_ZSET_KEY = "hot_foods"


async def record_food_query(food_name: str):
    """
    记录食物查询次数。
    使用 INCR 实现原子计数器 + 有序集合 ZINCRBY 实现排行榜。
    
    使用场景：每次查询食物详情时，原子性增加计数，用于展示"热门食物排行榜"。
    """
    # 原子计数器：INCR
    await redis_client.increment(f"{FOOD_QUERY_COUNTER_PREFIX}:{food_name}")
    # 有序集合：ZINCRBY（用于排行榜）
    await redis_client.zincrby(HOT_FOODS_ZSET_KEY, 1, food_name)


async def get_hot_foods(top_n: int = 10) -> list:
    """
    获取热门食物排行榜。
    从 Redis 有序集合中按分数从高到低获取。
    
    返回列表，每项为 (food_name, count) 元组。
    """
    results = await redis_client.zrevrange(HOT_FOODS_ZSET_KEY, 0, top_n - 1)
    return [(item[0], int(item[1])) for item in results]


async def get_food_query_count(food_name: str) -> int:
    """获取单个食物查询次数"""
    return await redis_client.get_counter(f"{FOOD_QUERY_COUNTER_PREFIX}:{food_name}")