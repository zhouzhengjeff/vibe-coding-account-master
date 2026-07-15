"""报表 Schema"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationInfo, field_validator


class SummaryCard(BaseModel):
    """汇总卡片"""
    label: str
    value: Decimal
    change_percent: Decimal | None = None
    trend: str | None = None  # "up", "down", "flat"


class CategoryBreakdown(BaseModel):
    """分类占比"""
    category: str
    amount: Decimal
    percentage: Decimal
    icon: str | None = None


class DailyTrend(BaseModel):
    """每日趋势"""
    date: str
    amount: Decimal


class WeeklyReport(BaseModel):
    """周报表数据"""
    summary: dict[str, SummaryCard]
    daily_expense_trend: list[DailyTrend]
    expense_by_category: list[CategoryBreakdown]
    income_by_category: list[CategoryBreakdown]
    avg_daily_spending: Decimal
    week_label: str  # e.g. "2026-07-13 ~ 2026-07-19"


class MonthlyReport(BaseModel):
    """月报表数据"""
    summary: dict[str, SummaryCard]
    daily_expense_trend: list[DailyTrend]
    daily_income_trend: list[DailyTrend]
    category_ranking: list[CategoryBreakdown]
    budget_progress: list[dict]  # {category, limit, spent, percent}
    month_label: str  # e.g. "2026-07"
    largest_expense: dict | None = None  # {amount, category, date, remark}
    most_frequent_category: str | None = None


class CustomReportRequest(BaseModel):
    """自定义报表请求"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    dimension: str = Field("category", description="统计维度: category, payment_method")

    @field_validator("end_date")
    @classmethod
    def validate_span(cls, v: date, info: "ValidationInfo") -> date:
        if v < info.data.get("start_date"):
            raise ValueError("结束日期不能早于开始日期")
        delta = (v - info.data["start_date"]).days
        if delta > 365:
            raise ValueError("时间跨度不能超过1年")
        return v


class CustomReport(BaseModel):
    """自定义报表数据"""
    summary: dict[str, SummaryCard]
    breakdown: list[CategoryBreakdown]
    start_date: str
    end_date: str
    dimension: str
