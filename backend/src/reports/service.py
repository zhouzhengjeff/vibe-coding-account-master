"""报表业务逻辑 — 聚合查询、统计分析"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Sequence

from src.shared.database import get_async_session
from src.shared.exceptions import AppError
from src.shared.logging_config import get_logger
from src.transactions.models import Transaction, TransactionType

logger = get_logger(__name__)


class ReportService:
    """报表服务 — 周/月/自定义维度聚合"""

    # 预设分类图标映射
    CATEGORY_ICONS: dict[str, str] = {
        "餐饮美食": "🍜", "交通出行": "🚗", "购物消费": "🛒",
        "住房租金": "🏠", "水电缴费": "💡", "娱乐休闲": "🎮",
        "医疗健康": "💊", "教育学习": "📚", "通讯费用": "📱",
        "人情往来": "🎁", "其他支出": "📝",
        "工资薪金": "💰", "奖金/提成": "🏆", "投资收益": "📈",
        "兼职收入": "💼", "退款/报销": "↩️", "其他收入": "💵",
    }

    async def get_weekly_report(
        self,
        user_id: int,
        target_date: date | None = None,
    ) -> dict:
        """获取周报表（默认本周）"""
        today = target_date or date.today()
        # 计算本周周一
        weekday = today.weekday()  # 0=Mon
        week_start = today - timedelta(days=weekday)
        week_end = week_start + timedelta(days=6)

        # 上周范围
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start - timedelta(days=1)

        total_income, total_expense = await self._calc_totals(user_id, week_start, week_end)
        last_total_income, last_total_expense = await self._calc_totals(user_id, last_week_start, last_week_end)

        # 每日支出趋势
        daily_expense = await self._daily_trend(user_id, week_start, week_end, TransactionType.EXPENSE)
        daily_income = await self._daily_trend(user_id, week_start, week_end, TransactionType.INCOME)

        # 分类占比
        expense_breakdown = await self._category_breakdown(user_id, week_start, week_end, TransactionType.EXPENSE)
        income_breakdown = await self._category_breakdown(user_id, week_start, week_end, TransactionType.INCOME)

        # 日均消费
        days_in_week = (week_end - week_start).days + 1
        avg_daily = total_expense / days_in_week if days_in_week > 0 else Decimal("0")

        # 环比
        if last_total_expense > 0:
            change = ((total_expense - last_total_expense) / last_total_expense * 100).quantize(Decimal("0.1"))
        elif total_expense > 0:
            change = Decimal("100.0")
        else:
            change = Decimal("0")

        return {
            "summary": {
                "total_income": self._make_card(total_income, "总收入", change if total_income > last_total_income else None, "up" if total_income > last_total_income else "down"),
                "total_expense": self._make_card(total_expense, "总支出", change),
                "balance": self._make_card(total_income - total_expense, "结余"),
            },
            "daily_expense_trend": [self._trend_item(d, a) for d, a in daily_expense],
            "daily_income_trend": [self._trend_item(d, a) for d, a in daily_income],
            "expense_by_category": self._breakdown_list(expense_breakdown),
            "income_by_category": self._breakdown_list(income_breakdown),
            "avg_daily_spending": avg_daily,
            "week_label": f"{week_start} ~ {week_end}",
            "week_start": str(week_start),
            "week_end": str(week_end),
            "change_percent": change,
        }

    async def get_monthly_report(
        self,
        user_id: int,
        target_date: date | None = None,
    ) -> dict:
        """获取月报表（默认本月）"""
        today = target_date or date.today()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        total_income, total_expense = await self._calc_totals(user_id, month_start, month_end)
        balance = total_income - total_expense
        savings_rate = (balance / total_income * 100).quantize(Decimal("0.1")) if total_income > 0 else Decimal("0")

        # 上月对比
        if today.month == 1:
            last_month_start = today.replace(year=today.year - 1, month=12, day=1)
            last_month_end = today.replace(year=today.year - 1, month=12, day=31)
        else:
            last_month_start = today.replace(month=today.month - 1, day=1)
            last_month_end = today.replace(month=today.month - 1, day=1) + timedelta(days=31)
            if last_month_end > today.replace(month=today.month - 1, day=1).replace(day=28):
                # 取实际月末
                last_month_end = last_month_end.replace(day=28) if today.month in (3, 5, 8, 10) else last_month_end

        last_income, last_expense = await self._calc_totals(user_id, last_month_start, last_month_end)

        daily_expense = await self._daily_trend(user_id, month_start, month_end, TransactionType.EXPENSE)
        daily_income = await self._daily_trend(user_id, month_start, month_end, TransactionType.INCOME)
        expense_breakdown = await self._category_breakdown(user_id, month_start, month_end, TransactionType.EXPENSE)

        # 最大单笔消费
        largest = await self._largest_expense(user_id, month_start, month_end)

        return {
            "summary": {
                "total_income": self._make_card(total_income, "总收入"),
                "total_expense": self._make_card(total_expense, "总支出"),
                "balance": self._make_card(balance, "结余"),
                "savings_rate": self._make_card(savings_rate, "储蓄率", unit="%"),
            },
            "monthly_comparison": {
                "income_change": self._calc_change(total_income, last_income),
                "expense_change": self._calc_change(total_expense, last_expense),
            },
            "daily_expense_trend": [self._trend_item(d, a) for d, a in daily_expense],
            "daily_income_trend": [self._trend_item(d, a) for d, a in daily_income],
            "category_ranking": self._breakdown_list_sorted(expense_breakdown),
            "largest_expense": largest,
            "month_label": f"{today.year}-{today.month:02d}",
        }

    async def get_custom_report(
        self,
        user_id: int,
        start_date: date,
        end_date: date,
        dimension: str = "category",
    ) -> dict:
        """自定义时间范围报表"""
        total_income, total_expense = await self._calc_totals(user_id, start_date, end_date)
        balance = total_income - total_expense

        breakdown = await self._category_breakdown(user_id, start_date, end_date, TransactionType.EXPENSE)

        return {
            "summary": {
                "total_income": self._make_card(total_income, "总收入"),
                "total_expense": self._make_card(total_expense, "总支出"),
                "balance": self._make_card(balance, "结余"),
            },
            "breakdown": self._breakdown_list(breakdown),
            "start_date": str(start_date),
            "end_date": str(end_date),
            "dimension": dimension,
        }

    # ---- 私有辅助方法 ----

    async def _calc_totals(
        self, user_id: int, start: date, end: date
    ) -> tuple[Decimal, Decimal]:
        """计算区间总收入和总支出，返回 (total_income, total_expense)"""
        async with get_async_session() as session:
            from sqlalchemy import func, select, and_

            result = await session.execute(
                select(
                    func.coalesce(func.sum(
                        func.case((Transaction.type == TransactionType.INCOME, Transaction.amount), else_=0)
                    ), 0),
                    func.coalesce(func.sum(
                        func.case((Transaction.type == TransactionType.EXPENSE, Transaction.amount), else_=0)
                    ), 0),
                ).where(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.date >= str(start),
                        Transaction.date <= str(end),
                    )
                )
            )
            row = result.one()
            return Decimal(str(row[0])), Decimal(str(row[1]))

    async def _daily_trend(
        self,
        user_id: int,
        start: date,
        end: date,
        txn_type: TransactionType,
    ) -> list[tuple[str, Decimal]]:
        """获取每日趋势"""
        async with get_async_session() as session:
            from sqlalchemy import func, select

            stmt = select(
                Transaction.date,
                func.coalesce(func.sum(Transaction.amount), 0),
            ).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == txn_type,
                    Transaction.date >= str(start),
                    Transaction.date <= str(end),
                )
            ).group_by(Transaction.date).order_by(Transaction.date)

            result = await session.execute(stmt)
            return [(str(r[0]), Decimal(str(r[1]))) for r in result]

    async def _category_breakdown(
        self,
        user_id: int,
        start: date,
        end: date,
        txn_type: TransactionType,
    ) -> list[tuple[str, Decimal]]:
        """获取分类占比"""
        async with get_async_session() as session:
            from sqlalchemy import func, select

            stmt = select(
                Transaction.category,
                func.coalesce(func.sum(Transaction.amount), 0),
            ).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == txn_type,
                    Transaction.date >= str(start),
                    Transaction.date <= str(end),
                )
            ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc())

            result = await session.execute(stmt)
            return [(r[0], Decimal(str(r[1]))) for r in result]

    async def _largest_expense(
        self, user_id: int, start: date, end: date
    ) -> dict | None:
        """获取最大单笔消费"""
        async with get_async_session() as session:
            from sqlalchemy import select

            stmt = (
                select(Transaction)
                .where(
                    and_(
                        Transaction.user_id == user_id,
                        Transaction.type == TransactionType.EXPENSE,
                        Transaction.date >= str(start),
                        Transaction.date <= str(end),
                    )
                )
                .order_by(Transaction.amount.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()
            if txn:
                return {
                    "amount": str(txn.amount),
                    "category": txn.category,
                    "date": str(txn.date),
                    "remark": txn.remark,
                }
            return None

    @staticmethod
    def _make_card(value: Decimal, label: str, change: Decimal | None = None, trend: str | None = None, unit: str = "") -> dict:
        """构造汇总卡片"""
        return {
            "label": label,
            "value": str(value),
            "change_percent": str(change) if change is not None else None,
            "trend": trend,
            "unit": unit,
        }

    @staticmethod
    def _calc_change(current: Decimal, previous: Decimal) -> dict:
        """计算环比变化"""
        if previous == 0:
            return {"percent": "0", "trend": "flat"}
        pct = ((current - previous) / previous * 100).quantize(Decimal("0.1"))
        return {"percent": str(pct), "trend": "up" if pct > 0 else "down" if pct < 0 else "flat"}

    @staticmethod
    def _trend_item(d: str, a: Decimal) -> dict:
        return {"date": d, "amount": str(a)}

    @staticmethod
    def _breakdown_list(items: list[tuple[str, Decimal]]) -> list[dict]:
        total = sum(v for _, v in items) if items else Decimal("0")
        result = []
        for cat, amt in items:
            pct = (amt / total * 100).quantize(Decimal("0.1")) if total > 0 else Decimal("0")
            result.append({
                "category": cat,
                "amount": str(amt),
                "percentage": str(pct),
                "icon": ReportService.CATEGORY_ICONS.get(cat),
            })
        return result

    @staticmethod
    def _breakdown_list_sorted(items: list[tuple[str, Decimal]]) -> list[dict]:
        """排序后的分类占比"""
        return sorted(ReportService._breakdown_list(items), key=lambda x: float(x["amount"]), reverse=True)
