"""预算模型"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Date, Decimal, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models import Base, TimestampMixin


class Budget(TimestampMixin, Base):
    """预算表 — 对应 budgets"""

    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    monthly_limit: Mapped[Decimal] = mapped_column(Decimal(12, 2), nullable=False)
    period_start: Mapped[str] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uk_user_category"),
    )

    def __repr__(self) -> str:
        return f"<Budget user_id={self.user_id} category={self.category}>"
