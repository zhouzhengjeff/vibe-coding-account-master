"""交易记录业务逻辑"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Sequence

from src.shared.database import get_async_session
from src.shared.exceptions import AppError, NotFoundError
from src.shared.logging_config import get_logger
from src.transactions.models import Transaction, TransactionType
from src.transactions.schemas import TransactionCreate, TransactionListParams, TransactionUpdate

logger = get_logger(__name__)


class TransactionService:
    """交易记录服务"""

    async def create(
        self, user_id: int, data: TransactionCreate
    ) -> Transaction:
        """创建交易记录"""
        async with get_async_session() as session:
            txn = Transaction(
                user_id=user_id,
                amount=data.amount,
                type=data.type,
                category=data.category,
                date=str(data.date),
                payment_method=data.payment_method,
                remark=data.remark,
            )
            session.add(txn)
            await session.commit()
            await session.refresh(txn)
            logger.info("transaction_created", user_id=user_id, txn_id=txn.id, amount=txn.amount)
            return txn

    async def get_by_id(self, user_id: int, txn_id: int) -> Transaction:
        """获取单条交易（校验归属）"""
        async with get_async_session() as session:
            from sqlalchemy import select
            stmt = select(Transaction).where(
                Transaction.id == txn_id,
                Transaction.user_id == user_id,
            )
            result = await session.execute(stmt)
            txn = result.scalar_one_or_none()
            if not txn:
                raise NotFoundError("Transaction", str(txn_id))
            return txn

    async def update(self, user_id: int, txn_id: int, data: TransactionUpdate) -> Transaction:
        """更新交易记录"""
        txn = await self.get_by_id(user_id, txn_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(txn, field, value)

        async with get_async_session() as session:
            session.add(txn)
            await session.commit()
            await session.refresh(txn)
            logger.info("transaction_updated", user_id=user_id, txn_id=txn_id)
            return txn

    async def delete(self, user_id: int, txn_id: int) -> None:
        """删除交易记录"""
        txn = await self.get_by_id(user_id, txn_id)
        async with get_async_session() as session:
            await session.delete(txn)
            await session.commit()
        logger.info("transaction_deleted", user_id=user_id, txn_id=txn_id)

    async def list_transactions(
        self,
        user_id: int,
        params: TransactionListParams,
    ) -> tuple[list[Transaction], int]:
        """分页查询交易列表"""
        async with get_async_session() as session:
            from sqlalchemy import func, select

            stmt = (
                select(Transaction)
                .where(Transaction.user_id == user_id)
            )

            # 筛选
            if params.type:
                stmt = stmt.where(Transaction.type == params.type)
            if params.category:
                stmt = stmt.where(Transaction.category == params.category)
            if params.start_date:
                stmt = stmt.where(Transaction.date >= str(params.start_date))
            if params.end_date:
                stmt = stmt.where(Transaction.date <= str(params.end_date))
            if params.search:
                stmt = stmt.where(Transaction.remark.contains(params.search))

            # 总数
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total_result = await session.execute(count_stmt)
            total = total_result.scalar()

            # 排序
            sort_field = getattr(Transaction, params.sort_by, Transaction.date) if hasattr(Transaction, params.sort_by) else Transaction.date
            if params.sort_order == "asc":
                stmt = stmt.order_by(sort_field.asc())
            else:
                stmt = stmt.order_by(sort_field.desc())

            # 分页
            offset = (params.page - 1) * params.page_size
            stmt = stmt.offset(offset).limit(params.page_size)

            result = await session.execute(stmt)
            items = list(result.scalars().all())
            return items, total or 0
