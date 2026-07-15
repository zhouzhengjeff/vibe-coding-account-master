"""报表路由"""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query, Request

from src.reports.schemas import CustomReportRequest
from src.reports.service import ReportService
from src.shared.dependencies import get_current_user_id

router = APIRouter(prefix="/api/reports", tags=["报表"])


@router.get("/weekly")
async def weekly_report(
    request: Request,
    service: ReportService = Depends(),
    year: int = Query(date.today().year),
    week: int = Query(1, ge=1, le=52),
) -> dict:
    """获取周报表"""
    user_id = await get_current_user_id(request)
    # 计算目标周的日期
    from datetime import datetime as dt
    target = dt.isocalendar(dt(year, week, 1))[0:2]  # rough
    target_date = date(year, 1, 1)
    # 找到目标周的周一
    week_monday = target_date + timedelta(days=(week - 1) * 7)
    weekday = week_monday.weekday()
    week_start = week_monday - timedelta(days=weekday)

    return await service.get_weekly_report(user_id, target_date=week_start)


@router.get("/monthly")
async def monthly_report(
    request: Request,
    service: ReportService = Depends(),
    year: int = Query(date.today().year),
    month: int = Query(date.today().month, ge=1, le=12),
) -> dict:
    """获取月报表"""
    user_id = await get_current_user_id(request)
    target_date = date(year, month, 1)
    return await service.get_monthly_report(user_id, target_date=target_date)


@router.get("/custom")
async def custom_report(
    request: Request,
    service: ReportService = Depends(),
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    dimension: str = Query("category", description="统计维度"),
) -> dict:
    """自定义时间范围报表"""
    user_id = await get_current_user_id(request)
    sd = date.fromisoformat(start_date)
    ed = date.fromisoformat(end_date)
    return await service.get_custom_report(user_id, sd, ed, dimension)
