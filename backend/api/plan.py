"""
减脂规划 API 接口。
"""
from fastapi import APIRouter, HTTPException, Request
from backend.models.schemas import PlanRequest, PlanResponse
from backend.services.plan_service import get_or_generate_plan
from backend.services.limiter_service import check_rate_limit

router = APIRouter(prefix="/api/plan", tags=["减脂规划"])


@router.post("/generate", response_model=PlanResponse)
async def generate_plan_api(req: PlanRequest, request: Request):
    """
    生成个性化减脂规划。
    限流策略：每 IP 每分钟 10 次（令牌桶/滑动窗口）。
    缓存策略：按参数哈希缓存 1 天。
    """
    # 限流检查
    client_ip = request.client.host if request.client else "unknown"
    allowed = await check_rate_limit(client_ip, "/api/plan/generate", max_requests=10, window_seconds=60)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="请求过于频繁，请稍后再试（每 IP 每分钟限制 10 次）"
        )
    
    plan = await get_or_generate_plan(req)
    return plan