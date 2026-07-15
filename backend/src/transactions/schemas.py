"""交易记录 Schema"""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from src.transactions.models import TransactionType


class TransactionCreate(BaseModel):
    """创建交易请求"""
    amount: Decimal = Field(..., gt=0, description="金额，必须大于0")
    type: TransactionType = Field(..., description="INCOME 或 EXPENSE")
    category: str = Field(..., min_length=1, max_length=50, description="分类")
    date: date_type = Field(default_factory=date_type.today, description="交易日期")
    payment_method: str | None = Field(None, max_length=50, description="支付方式")
    remark: str = Field("", max_length=200, description="备注")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("金额必须大于0")
        if v.quantize(Decimal("0.01")) != v:
            raise ValueError("金额最多保留两位小数")
        return v


class TransactionUpdate(BaseModel):
    """更新交易请求 — 所有字段可选"""
    amount: Decimal | None = Field(None, gt=0, description="金额")
    type: TransactionType | None = None
    category: str | None = Field(None, min_length=1, max_length=50)
    date: date_type | None = None
    payment_method: str | None = Field(None, max_length=50)
    remark: str | None = Field(None, max_length=200)


class TransactionOut(BaseModel):
    """交易记录响应"""
    id: int
    user_id: int
    amount: Decimal
    type: TransactionType
    category: str
    date: str
    payment_method: str | None
    remark: str
    created_at: str

    model_config = {"from_attributes": True}


class TransactionListParams(BaseModel):
    """交易列表查询参数"""
    type: TransactionType | None = None
    category: str | None = None
    start_date: date_type | None = None
    end_date: date_type | None = None
    search: str | None = None
    sort_by: str = "date"
    sort_order: str = "desc"
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页条数")
