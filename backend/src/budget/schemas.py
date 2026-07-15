"""预算 Schema"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetCreate(BaseModel):
    """创建预算请求"""
    category: str = Field(..., min_length=1, max_length=50)
    monthly_limit: Decimal = Field(..., gt=0, description="月度预算限额")
    period_start: date = Field(default_factory=date.today, description="统计周期开始")


class BudgetOut(BaseModel):
    """预算响应"""
    id: int
    user_id: int
    category: str
    monthly_limit: Decimal
    period_start: str
    spent: Decimal = Decimal("0")  # 已花费
    remaining: Decimal = Decimal("0")  # 剩余
    progress: Decimal = Decimal("0")  # 进度百分比

    model_config = {"from_attributes": True}
