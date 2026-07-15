"""用户模块路由"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.auth.schemas import UserOut
from src.shared.dependencies import get_current_user_id
from src.user.schemas import UserProfileUpdate

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/profile", response_model=UserOut)
async def get_profile(request: Request) -> UserOut:
    """获取用户资料"""
    user_id = await get_current_user_id(request)
    from src.auth.service import AuthService
    service = AuthService()
    user = await service.get_user_by_id(user_id)
    return UserOut.model_validate(user)


@router.put("/profile", response_model=UserOut)
async def update_profile(
    request: Request,
    data: UserProfileUpdate,
) -> UserOut:
    """更新用户资料"""
    user_id = await get_current_user_id(request)
    from src.shared.database import get_async_session
    from src.auth.models import User
    from sqlalchemy import select

    async with get_async_session() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            from src.shared.exceptions import NotFoundError
            raise NotFoundError("User", str(user_id))

        user.nickname = data.nickname
        user.avatar_url = data.avatar_url
        user.currency = data.currency

        session.add(user)
        await session.commit()
        await session.refresh(user)

    return UserOut.model_validate(user)
