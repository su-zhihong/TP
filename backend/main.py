"""
智能营养与减脂规划助手 - FastAPI 主入口
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.config import settings
from backend.core.redis_client import redis_client
from backend.db.neo4j_client import neo4j_client
from backend.api import foods, qa, plan, stats, admin
from backend.utils.bloom_filter import food_bloom
from backend.services.graph_service import get_all_food_names
from backend.db.postgres_client import init_db


async def startup():
    """应用启动时的初始化操作"""
    print("🚀 正在初始化服务...")
    
    # 1. 初始化 Redis 连接
    try:
        await redis_client.initialize()
        print("✅ Redis 连接成功")
    except Exception as e:
        print(f"⚠️ Redis 连接失败（如未安装 Redis，部分功能不可用）: {e}")
    
    # 2. 初始化 Neo4j 连接
    neo4j_available = False
    try:
        await neo4j_client.initialize()
        print("✅ Neo4j 连接成功")
        neo4j_available = True
    except Exception as e:
        print(f"⚠️ Neo4j 连接失败（使用内置数据）: {e}")
    
    # 初始化布隆过滤器
    try:
        food_names = []
        if neo4j_available:
            food_names = await get_all_food_names()
        
        # 如果 Neo4j 不可用，从后端内置数据加载食物名称
        if not food_names:
            from backend.api.foods import BUILTIN_FOODS
            food_names = [f["name"] for f in BUILTIN_FOODS]
            print(f"📦 从内置数据加载 {len(food_names)} 种食物")
        
        for name in food_names:
            food_bloom.add(name)
        print(f"✅ 布隆过滤器初始化完成，已加载 {len(food_names)} 种食物")
        
        # 同步到 Redis（供 API 使用）
        for name in food_names:
            await redis_client.bloom_add("food_names", name)
    except Exception as e:
        print(f"⚠️ 布隆过滤器初始化失败: {e}")
    
    # 3. 初始化 SQLite 数据库
    try:
        await init_db()
        print("✅ SQLite 数据库初始化完成")
    except Exception as e:
        print(f"⚠️ SQLite 初始化失败: {e}")
    
    print("🎉 服务启动完成！")


async def shutdown():
    """应用关闭时的清理操作"""
    await redis_client.close()
    await neo4j_client.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()


app = FastAPI(
    title="智能营养与减脂规划助手",
    description="知识图谱 + RAG + Redis 高并发缓存的减脂智能助手",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册 API 路由
app.include_router(foods.router)
app.include_router(qa.router)
app.include_router(plan.router)
app.include_router(stats.router)
app.include_router(admin.router)


# 前端静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")


@app.get("/")
async def root():
    """首页：返回前端 HTML 页面"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "智能营养与减脂规划助手",
        "version": "1.0.0",
        "status": "running",
        "message": "前端页面未找到，请确保 frontend/index.html 存在"
    }


@app.get("/health")
async def health():
    """健康检查端点"""
    return {
        "service": "智能营养与减脂规划助手",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "首页": "/（前端页面）",
            "健康检查": "/health",
            "搜索食物": "/api/foods?keyword=xxx",
            "食物详情": "/api/foods/{name}",
            "知识图谱": "/api/foods/{name}/graph",
            "智能问答": "/api/qa/ask",
            "减脂规划": "/api/plan/generate",
            "热门食物": "/api/stats/hot_foods",
            "刷新缓存": "/api/admin/refresh_cache/food/{name}"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器内部错误: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)