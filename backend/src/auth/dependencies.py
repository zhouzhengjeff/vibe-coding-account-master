"""认证依赖 — 从请求中提取并验证 JWT"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status

from src.auth.utils import decode_token, get_user_id_from_token
from src.shared.exceptions import AuthenticationError


async def get_current_user_id(request: Request) -> int:
    """从 Authorization header 提取并验证 access token"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise AuthenticationError("Missing or invalid Authorization header")

    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise AuthenticationError("Invalid token type")
        return int(payload["sub"])
    except (ValueError, KeyError) as exc:
        if isinstance(exc, AuthenticationError):
            raise
        raise AuthenticationError("Invalid or expired token") from exc


def require_auth(request: Request) -> int:
    """FastAPI 依赖注入：需要认证的端点使用"""
    return get_current_user_id(request)


async def get_optional_user_id(request: Request) -> int | None:
    """可选认证：有 token 就解析，没有就返回 None"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return int(payload["sub"])
    except (ValueError, KeyError, AuthenticationError):
        return None
