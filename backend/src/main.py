"""日常记账App — FastAPI 应用入口"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保 src 在 Python path 中
sys.path.insert(0, str(Path(__file__).parent / "src"))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.middleware.error_handler import register_exception_handlers
from src.middleware import register_middleware
from src.shared.config import settings
from src.shared.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(
        "starting_app",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    yield
    logger.info("shutting_down_app")


def create_app() -> FastAPI:
    """应用工厂"""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # 注册中间件和异常处理器
    register_middleware(app)
    register_exception_handlers(app)

    # 注册路由
    from src.auth.router import router as auth_router
    from src.transactions.router import router as transactions_router
    from src.reports.router import router as reports_router
    from src.user.router import router as user_router
    from src.budget.router import router as budget_router

    app.include_router(auth_router)
    app.include_router(transactions_router)
    app.include_router(reports_router)
    app.include_router(user_router)
    app.include_router(budget_router)

    # 健康检查
    @app.get("/health")
    async def health_check() -> dict:
        return {"status": "ok", "version": settings.app_version}

    @app.get("/ready")
    async def readiness_check() -> JSONResponse:
        """就绪检查（可扩展数据库连接检测）"""
        return JSONResponse(content={"status": "ok", "checks": {"database": "ok"}})

    return app


app = create_app()
