"""中间件模块"""

from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from src.shared.config import settings
from src.shared.logging_config import get_logger

logger = get_logger(__name__)


def register_middleware(app: FastAPI) -> None:
    """注册全局中间件"""

    # CORS
    import json
    try:
        origins = json.loads(settings.cors_origins)
    except (json.JSONDecodeError, TypeError):
        origins = ["http://localhost:5173"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Request ID + 日志
    @app.middleware("http")
    async def request_middleware(request: Request, call_next) -> JSONResponse | Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        request.state.request_id = request_id

        start = time.time()
        response = await call_next(request)
        elapsed = time.time() - start

        logger.info(
            "http_request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(elapsed * 1000, 2),
        )
        response.headers["X-Request-ID"] = request_id
        return response
