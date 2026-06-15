"""
限流服务。
基于 Redis 滑动窗口实现令牌桶限流，使用 Lua 脚本保证原子性。
"""
from backend.core.redis_client import redis_client


async def check_rate_limit(ip: str, endpoint: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    """
    检查请求是否超过限流阈值。
    使用滑动窗口算法，Lua 脚本保证原子性。
    
    使用场景：/api/plan/generate 接口每 IP 每分钟 10 次。
    
    Args:
        ip: 客户端 IP
        endpoint: 接口路径
        max_requests: 窗口内最大请求数
        window_seconds: 窗口大小（秒）
    
    Returns:
        True 表示允许请求，False 表示限流
    """
    key = f"ratelimit:{endpoint}:{ip}"
    return await redis_client.allow_request(key, max_requests, window_seconds)