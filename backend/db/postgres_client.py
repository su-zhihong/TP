"""
PostgreSQL 客户端封装（可选）。
用于存储用户减脂规划历史。
"""
import json
from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime

# 使用 SQLite 替代 PostgreSQL 便于开发
DATABASE_URL = "sqlite+aiosqlite:///./nutrition.db"


class Base(DeclarativeBase):
    pass


class UserPlan(Base):
    __tablename__ = "user_plans"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    params_json = Column(Text, comment="用户输入的参数JSON")
    result_json = Column(Text, comment="规划结果JSON")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession)


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_user_plan(params: dict, result: dict):
    """保存用户规划历史"""
    async with async_session() as session:
        plan = UserPlan(
            params_json=json.dumps(params, ensure_ascii=False),
            result_json=json.dumps(result, ensure_ascii=False)
        )
        session.add(plan)
        await session.commit()


async def get_user_plans(limit: int = 10) -> List[dict]:
    """获取最近规划历史"""
    async with async_session() as session:
        from sqlalchemy import select, desc
        result = await session.execute(
            select(UserPlan).order_by(desc(UserPlan.created_at)).limit(limit)
        )
        plans = result.scalars().all()
        return [
            {
                "id": p.id,
                "params": json.loads(p.params_json),
                "result": json.loads(p.result_json),
                "created_at": p.created_at.isoformat()
            }
            for p in plans
        ]