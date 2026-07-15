"""数据库引擎与会话工厂"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.shared.config import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    """FastAPI 依赖：注入异步数据库会话"""
    async with async_session_factory() as session:
        yield session
