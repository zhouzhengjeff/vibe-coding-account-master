"""认证请求/响应 Schema"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

import re


class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")

    @staticmethod
    def _validate_phone(phone: str) -> str:
        if not re.fullmatch(r"1[3-9]\d{9}", phone):
            raise ValueError("请输入有效的11位中国大陆手机号")
        return phone

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return cls._validate_phone(v)


class RegisterRequest(LoginRequest):
    """注册请求"""
    nickname: str = Field(default="", description="昵称，最长50字符")

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str) -> str:
        if len(v) > 50:
            raise ValueError("昵称不能超过50个字符")
        return v


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """用户信息响应"""
    id: int
    phone: str
    nickname: str
    avatar_url: str
    currency: str

    model_config = {"from_attributes": True}


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码，至少6位")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("新密码至少6位")
        return v
