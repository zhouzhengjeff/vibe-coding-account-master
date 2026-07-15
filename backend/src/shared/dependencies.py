"""共享依赖注入"""

from __future__ import annotations

from fastapi import Header, HTTPException, Request, status


async def get_current_user_id(
    request: Request,
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> int:
    """从 Authorization header 或 X-API-Key 提取 user_id"""
    if x_api_key:
        # 预留 API Key 认证
        return int(x_api_key)

    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"title": "AUTH_MISSING", "detail": "Missing or invalid Authorization header"},
        )

    token = auth.split(" ", 1)[1]
    return _decode_access_token(token)


def _decode_access_token(token: str) -> int:
    """解码 access token 并返回 user_id"""
    from src.auth.utils import decode_token

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"title": "INVALID_TOKEN_TYPE", "detail": "Not an access token"},
            )
        return int(payload["sub"])
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"title": "INVALID_TOKEN", "detail": "Invalid or expired token"},
        ) from exc
