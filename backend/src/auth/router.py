"""认证路由 — 登录、注册、刷新、登出"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.auth.schemas import LoginRequest, PasswordChangeRequest, RegisterRequest, TokenResponse, UserOut
from src.auth.service import AuthService
from src.auth.utils import create_refresh_token
from src.shared.dependencies import get_current_user_id

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    req: LoginRequest,
    service: AuthService = Depends(),
) -> TokenResponse:
    """手机号 + 密码登录"""
    try:
        access_token = await service.authenticate(req.phone, req.password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"title": "AUTH_FAILED", "detail": str(exc)},
        ) from exc
    refresh_token = create_refresh_token(service._last_user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    service: AuthService = Depends(),
) -> TokenResponse:
    """新用户注册"""
    try:
        access_token = await service.register_user(req.phone, req.password, req.nickname)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"title": "REGISTRATION_FAILED", "detail": str(exc)},
        ) from exc
    refresh_token = create_refresh_token(service._last_user_id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    service: AuthService = Depends(),
) -> TokenResponse:
    """使用 refresh token 换取新的 access token"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"title": "MISSING_TOKEN", "detail": "Missing refresh token"},
        )
    try:
        new_access = await service.refresh_access_token(auth.split(" ", 1)[1])
        new_refresh = create_refresh_token(service._last_user_id)
        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"title": "REFRESH_FAILED", "detail": str(exc)},
        ) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout():
    """登出（前端丢弃 token 即可）"""


@router.get("/me", response_model=UserOut)
async def get_me(
    request: Request,
    service: AuthService = Depends(),
) -> UserOut:
    """获取当前用户信息"""
    user_id = await get_current_user_id(request)
    user = await service.get_user_by_id(user_id)
    return UserOut.model_validate(user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    req: PasswordChangeRequest,
    request: Request,
    service: AuthService = Depends(),
) -> dict[str, str]:
    """修改密码"""
    user_id = await get_current_user_id(request)
    try:
        await service.change_password(user_id, req.old_password, req.new_password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"title": "PASSWORD_CHANGE_FAILED", "detail": str(exc)},
        ) from exc
    return {"detail": "Password changed successfully"}
