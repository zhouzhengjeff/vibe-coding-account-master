"""交易记录模型"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Date, Enum, ForeignKey, String
from sqlalchemy.dialects.mysql import DECIMAL as MySQLDECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models import Base, TimestampMixin

import enum


class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Transaction(TimestampMixin, Base):
    """交易记录表 — 对应 transactions"""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(MySQLDECIMAL(12, 2), nullable=False)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    date: Mapped[str] = mapped_column(Date, nullable=False, index=True)
    payment_method: Mapped[Optional[str]] = Column(String(50), nullable=True)
    remark: Mapped[str] = mapped_column(String(200), default="")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} type={self.type.value} amount={self.amount}>"
