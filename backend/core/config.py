"""
应用配置模块，读取 .env 环境变量。
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # LLM
    LLM_API_KEY: str = "ollama"
    LLM_MODEL: str = "llama2"
    LLM_BASE_URL: str = "http://localhost:11434/v1"

    # App
    APP_SECRET_KEY: str = "nutrition-helper-secret-key"
    CACHE_ENABLED: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()