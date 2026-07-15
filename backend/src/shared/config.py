"""配置管理 — pydantic-settings, 启动时 fail-fast"""

from __future__ import annotations

from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，所有值从环境变量读取"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 数据库
    database_url: str = Field(..., description="同步数据库连接串")
    async_database_url: str = Field(..., description="异步数据库连接串")

    # JWT
    jwt_secret_key: str = Field(..., description="JWT签名密钥")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # 服务
    app_name: str = "日常记账App"
    app_version: str = "1.0.0"
    port: int = 8000
    debug: bool = False

    # CORS
    cors_origins: str = '["http://localhost:5173"]'

    @field_validator("debug", mode="before")
    @classmethod
    def _parse_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        return bool(v)


# 全局单例
settings = Settings()  # type: ignore[call-arg]  # env_file provided via model_config
