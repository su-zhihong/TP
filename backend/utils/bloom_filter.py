"""
布隆过滤器（内存版）。
生产环境应使用 RedisBloom 模块（BF.ADD / BF.EXISTS）。
此处用 pybloom_live 实现，用于项目演示。
"""
from pybloom_live import BloomFilter
from typing import Set, Optional


class MemoryBloomFilter:
    """
    内存版布隆过滤器。
    用于预检查食物是否存在，避免无效查询穿透到数据库。
    生产环境应替换为 RedisBloom。
    """

    def __init__(self, capacity: int = 10000, error_rate: float = 0.01):
        self._filter = BloomFilter(capacity=capacity, error_rate=error_rate)
        self._items: Set[str] = set()

    def add(self, item: str):
        """向布隆过滤器添加元素"""
        self._filter.add(item)
        self._items.add(item)

    def exists(self, item: str) -> bool:
        """
        检查元素是否可能存在。
        返回 False 表示一定不存在，返回 True 表示可能存在（有误判率）。
        """
        return item in self._filter

    @property
    def all_items(self) -> Set[str]:
        return self._items


# 全局单例：食物名称布隆过滤器
food_bloom = MemoryBloomFilter(capacity=10000, error_rate=0.01)