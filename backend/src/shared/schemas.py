"""共享响应模型"""

from __future__ import annotations

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """成功响应"""
    detail: str
    data: object | None = None


class ErrorResponse(BaseModel):
    """错误响应"""
    title: str
    detail: str
    status: int
    request_id: str | None = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: list[object]
    total: int
    page: int
    page_size: int
    total_pages: int
