from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class MaxBase(DeclarativeBase):
    pass


class MaxBadgeType(str, enum.Enum):
    hit = "hit"
    new = "new"
    premium = "premium"


class MaxLeadStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    rejected = "rejected"


class MaxProduct(MaxBase):
    __tablename__ = "max_products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    size_ft: Mapped[str] = mapped_column(String(16), nullable=False)  # "20ft" or "40ft"
    price_from: Mapped[int] = mapped_column(Integer, nullable=False)
    badge: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_max_products_active_sort", "is_active", "sort_order"),
    )


class MaxCalcSizeOption(MaxBase):
    __tablename__ = "max_calc_size_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    base_price: Mapped[int] = mapped_column(Integer, nullable=False)


class MaxCalcInsulationOption(MaxBase):
    __tablename__ = "max_calc_insulation_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class MaxCalcFinishingOption(MaxBase):
    __tablename__ = "max_calc_finishing_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class MaxCalcExtra(MaxBase):
    __tablename__ = "max_calc_extras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_max_extras_sort", "sort_order"),
    )


class MaxUser(MaxBase):
    __tablename__ = "max_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    leads: Mapped[list["MaxLead"]] = relationship(back_populates="user")


class MaxLead(MaxBase):
    __tablename__ = "max_leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("max_users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    calc_config: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[MaxLeadStatus] = mapped_column(
        SAEnum(MaxLeadStatus, name="max_lead_status"),
        nullable=False,
        default=MaxLeadStatus.new,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["MaxUser"] = relationship(back_populates="leads")

    __table_args__ = (
        Index("idx_max_leads_status", "status", "created_at"),
        Index("idx_max_leads_user", "user_id"),
    )
