"""
统计相关 API 接口。
展示 Redis 原子计数和热门排行榜功能。
"""
from fastapi import APIRouter
from backend.models.schemas import HotFoodsResponse, HotFoodItem
from backend.services.stats_service import get_hot_foods

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/hot_foods", response_model=HotFoodsResponse)
async def get_hot_foods_api():
    """
    获取热门食物排行榜。
    实时从 Redis 有序集合读取。
    """
    data = await get_hot_foods(top_n=10)
    foods = [HotFoodItem(name=name, query_count=count) for name, count in data]
    return HotFoodsResponse(foods=foods)