"""用户 Profile Schema"""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfileUpdate(BaseModel):
    """更新用户资料"""
    nickname: str = Field(..., min_length=1, max_length=50, description="昵称")
    avatar_url: str = Field("", max_length=500, description="头像URL")
    currency: str = Field("CNY", max_length=10, description="货币单位")


class UserSettings(BaseModel):
    """用户偏好设置"""
    dark_mode: bool = False
    week_start_day: str = "Monday"  # Monday | Sunday
    currency: str = "CNY"
