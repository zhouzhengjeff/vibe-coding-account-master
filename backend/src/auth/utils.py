"""JWT 工具 — 签发、验证、刷新"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from src.shared.config import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: int) -> str:
    """签发 Access Token"""
    expires = _now_utc() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expires, "type": "access"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """签发 Refresh Token"""
    expires = _now_utc() + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {"sub": str(user_id), "exp": expires, "type": "refresh"}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, object]:
    """解码并验证 Token，返回 payload"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as exc:
        raise ValueError(f"Invalid token: {exc}") from exc


def get_user_id_from_token(token: str) -> int:
    """从 token 中提取 user_id"""
    payload = decode_token(token)
    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Token missing user sub")
    return int(sub)
