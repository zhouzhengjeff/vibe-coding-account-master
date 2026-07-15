"""认证业务逻辑 — 密码哈希、用户 CRUD、JWT 签发"""

from __future__ import annotations

from src.auth.models import User
from src.auth.utils import create_access_token
from src.shared.database import get_async_session
from src.shared.exceptions import AppError, NotFoundError
from src.shared.logging_config import get_logger

logger = get_logger(__name__)


class AuthService:
    """认证服务 — 处理登录、注册、密码管理"""

    def __init__(self) -> None:
        self._last_user_id: int = 0

    async def authenticate(self, phone: str, password: str) -> str:
        """验证手机号+密码，返回 access token"""
        user = await self._find_user_by_phone(phone)
        if not user or not self._verify_password(password, user.password_hash):
            raise AppError("Invalid phone or password", "AUTH_FAILED", 401)
        self._last_user_id = user.id
        logger.info("user_login", user_id=user.id, phone=user.phone)
        return create_access_token(user.id)

    async def register_user(self, phone: str, password: str, nickname: str = "") -> str:
        """注册用户"""
        existing = await self._find_user_by_phone(phone)
        if existing:
            raise AppError("Phone already registered", "PHONE_EXISTS", 409)

        hashed = self._hash_password(password)
        user = User(phone=phone, password_hash=hashed, nickname=nickname or phone[:7])
        await self._save_user(user)
        self._last_user_id = user.id
        logger.info("user_registered", user_id=user.id, phone=user.phone)
        return create_access_token(user.id)

    async def refresh_access_token(self, refresh_token: str) -> str:
        """用 refresh token 签发新的 access token"""
        from src.auth.utils import decode_token

        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise AppError("Invalid token type", "INVALID_TOKEN", 401)
            user_id = int(payload["sub"])
        except (ValueError, KeyError) as exc:
            raise AppError("Invalid refresh token", "INVALID_TOKEN", 401) from exc

        user = await self._find_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        self._last_user_id = user.id
        return create_access_token(user.id)

    async def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        """修改密码"""
        user = await self._find_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        if not self._verify_password(old_password, user.password_hash):
            raise AppError("Old password is incorrect", "WRONG_PASSWORD", 400)
        user.password_hash = self._hash_password(new_password)
        await self._save_user(user)
        logger.info("password_changed", user_id=user_id)

    async def get_user_by_id(self, user_id: int) -> User:
        """按 ID 获取用户"""
        user = await self._find_user_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    # ---- 私有方法 ----

    async def _find_user_by_phone(self, phone: str) -> User | None:
        from sqlalchemy import select
        async with get_async_session() as session:
            stmt = select(User).where(User.phone == phone)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def _find_user_by_id(self, user_id: int) -> User | None:
        from sqlalchemy import select
        async with get_async_session() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def _save_user(self, user: User) -> None:
        async with get_async_session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)

    @staticmethod
    def _hash_password(password: str) -> str:
        """使用 bcrypt 哈希密码"""
        import bcrypt as bcrypt_lib
        return bcrypt_lib.hashpw(password.encode("utf-8"), bcrypt_lib.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """验证密码"""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False
