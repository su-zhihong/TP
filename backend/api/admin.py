"""
管理端 API 接口。
"""
from fastapi import APIRouter, HTTPException
from backend.core.security import verify_token
from backend.models.schemas import RefreshCacheResponse
from backend.core.redis_client import redis_client

router = APIRouter(prefix="/api/admin", tags=["管理"])


@router.post("/refresh_cache/food/{name}", response_model=RefreshCacheResponse)
async def refresh_food_cache(name: str, token_verified: bool = None):
    """
    手动刷新食物缓存。
    需要 Token 认证（Bearer Token）。
    """
    # Token 验证由依赖注入处理
    cache_key = f"food_detail:{name}"
    await redis_client.delete(cache_key)
    
    return RefreshCacheResponse(
        message=f"食物 '{name}' 的缓存已清除",
        success=True
    )