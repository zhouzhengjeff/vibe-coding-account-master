"""预算路由"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Request, status

from src.budget.schemas import BudgetCreate, BudgetOut
from src.shared.dependencies import get_current_user_id

router = APIRouter(prefix="/api/budgets", tags=["预算"])


@router.post("", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
async def create_budget(
    request: Request,
    data: BudgetCreate,
) -> BudgetOut:
    """创建/更新分类预算"""
    user_id = await get_current_user_id(request)
    from src.shared.database import get_async_session
    from src.budget.models import Budget
    from sqlalchemy import select, and_

    async with get_async_session() as session:
        # 确定本月周期
        today = date.today()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        stmt = select(Budget).where(
            and_(
                Budget.user_id == user_id,
                Budget.category == data.category,
            )
        )
        result = await session.execute(stmt)
        budget = result.scalar_one_or_none()

        if budget:
            budget.monthly_limit = data.monthly_limit
            budget.period_start = str(month_start)
        else:
            budget = Budget(
                user_id=user_id,
                category=data.category,
                monthly_limit=data.monthly_limit,
                period_start=str(month_start),
            )
            session.add(budget)

        await session.commit()
        await session.refresh(budget)

        # 计算已花费
        from src.transactions.models import Transaction, TransactionType
        from sqlalchemy import func, select as sa_select
        stmt2 = sa_select(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.category == data.category,
                Transaction.date >= str(month_start),
                Transaction.date <= str(month_end),
            )
        )
        spent_result = await session.execute(stmt2)
        spent = Decimal(str(spent_result.scalar()))

        limit = budget.monthly_limit
        remaining = max(limit - spent, Decimal("0"))
        progress = (spent / limit * 100).quantize(Decimal("0.1")) if limit > 0 else Decimal("0")

        return BudgetOut(
            id=budget.id,
            user_id=budget.user_id,
            category=budget.category,
            monthly_limit=budget.monthly_limit,
            period_start=budget.period_start,
            spent=spent,
            remaining=remaining,
            progress=progress,
        )


@router.get("")
async def list_budgets(
    request: Request,
) -> dict:
    """获取用户所有预算"""
    user_id = await get_current_user_id(request)
    from src.shared.database import get_async_session
    from src.budget.models import Budget
    from sqlalchemy import select

    async with get_async_session() as session:
        stmt = select(Budget).where(Budget.user_id == user_id)
        result = await session.execute(stmt)
        budgets = result.scalars().all()

        return {
            "items": [
                {
                    "id": b.id,
                    "category": b.category,
                    "monthly_limit": str(b.monthly_limit),
                    "period_start": str(b.period_start),
                }
                for b in budgets
            ]
        }
