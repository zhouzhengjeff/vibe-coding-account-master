"""用户模型"""

from __future__ import annotations

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.models import Base, TimestampMixin


class User(TimestampMixin, Base):
    """用户表 — 对应 users"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), default="")
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    currency: Mapped[str] = mapped_column(String(10), default="CNY")

    def __repr__(self) -> str:
        return f"<User id={self.id} phone={self.phone}>"
