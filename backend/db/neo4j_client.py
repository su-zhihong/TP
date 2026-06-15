"""
Neo4j 数据库客户端封装。
"""
from neo4j import AsyncGraphDatabase
from backend.core.config import settings


class Neo4jClient:
    def __init__(self):
        self._driver = None

    async def initialize(self):
        self._driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        # 验证连接
        async with self._driver.session() as session:
            result = await session.run("RETURN 1 as n")
            await result.single()

    async def close(self):
        if self._driver:
            await self._driver.close()

    @property
    def driver(self):
        if self._driver is None:
            raise RuntimeError("Neo4j driver not initialized.")
        return self._driver

    async def run(self, cypher: str, **params) -> list:
        async with self._driver.session() as session:
            result = await session.run(cypher, params)
            records = await result.data()
            return records


neo4j_client = Neo4jClient()