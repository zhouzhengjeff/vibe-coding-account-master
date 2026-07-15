"""全局异常处理器"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.shared.exceptions import AppError
from src.shared.logging_config import get_logger

logger = get_logger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        logger.warning(
            "app_error",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "title": exc.code,
                "detail": exc.message,
                "status": exc.status_code,
                "request_id": request_id,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        errors = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"] if loc not in ("body", "query", "path"))
            errors.append({"field": field, "message": err["msg"]})
        logger.warning(
            "validation_error",
            request_id=request_id,
            errors=errors,
        )
        return JSONResponse(
            status_code=422,
            content={
                "title": "VALIDATION_ERROR",
                "detail": "Request validation failed",
                "status": 422,
                "errors": errors,
                "request_id": request_id,
            },
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        errors = [{"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(
            status_code=422,
            content={
                "title": "VALIDATION_ERROR",
                "detail": "Validation failed",
                "status": 422,
                "errors": errors,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
        logger.error(
            "unexpected_error",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            error=str(exc),
            stack=getattr(exc, "__traceback__", None),
        )
        return JSONResponse(
            status_code=500,
            content={
                "title": "INTERNAL_ERROR",
                "detail": "An unexpected error occurred",
                "status": 500,
                "request_id": request_id,
            },
        )
