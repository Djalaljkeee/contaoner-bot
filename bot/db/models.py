from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
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


class Base(DeclarativeBase):
    pass


class ProductType(str, enum.Enum):
    house = "house"
    office = "office"


class ContainerSpec(str, enum.Enum):
    ft20 = "20ft"
    ft40 = "40ft"
    x2ft40 = "2x40ft"
    x3ft40 = "3x40ft"


class BadgeType(str, enum.Enum):
    hit = "hit"
    new = "new"
    premium = "premium"


class CalcOptionGroup(str, enum.Enum):
    module = "module"
    insulation = "insulation"
    foundation = "foundation"
    interior = "interior"
    windows = "windows"


class LeadType(str, enum.Enum):
    regular = "regular"
    preorder = "preorder"
    calculator = "calculator"


class LeadStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    rejected = "rejected"


class LeadSource(str, enum.Enum):
    main_menu = "main_menu"
    product_card = "product_card"
    calculator = "calculator"
    contacts = "contacts"


class AdminRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"


class BroadcastStatus(str, enum.Enum):
    draft = "draft"
    sending = "sending"
    sent = "sent"
    failed = "failed"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[ProductType] = mapped_column(
        SAEnum(ProductType, name="product_type"), nullable=False
    )
    container_spec: Mapped[ContainerSpec] = mapped_column(
        SAEnum(ContainerSpec, name="container_spec"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    area_m2: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    price_from: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    build_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    badge: Mapped[Optional[BadgeType]] = mapped_column(
        SAEnum(BadgeType, name="badge_type"), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    photos: Mapped[list["ProductPhoto"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductPhoto.sort_order",
    )

    __table_args__ = (
        Index("idx_products_type_spec", "type", "container_spec", "is_active", "sort_order"),
    )


class ProductPhoto(Base):
    __tablename__ = "product_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    local_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_cover: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product: Mapped[Product] = relationship(back_populates="photos")

    __table_args__ = (
        CheckConstraint(
            "file_id IS NOT NULL OR local_path IS NOT NULL OR source_url IS NOT NULL",
            name="ck_photo_has_source",
        ),
        Index("idx_photos_product", "product_id", "sort_order"),
    )


class CalcOption(Base):
    __tablename__ = "calc_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group: Mapped[CalcOptionGroup] = mapped_column(
        SAEnum(CalcOptionGroup, name="calc_option_group"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price_delta: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    area_m2: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        Index("idx_calc_opts_group", "group", "is_active", "sort_order"),
    )


class DeliveryCity(Base):
    __tablename__ = "delivery_cities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    distance_km: Mapped[int] = mapped_column(Integer, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_subscribed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[AdminRole] = mapped_column(SAEnum(AdminRole, name="admin_role"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[LeadType] = mapped_column(
        SAEnum(LeadType, name="lead_type"), nullable=False, default=LeadType.regular
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    calc_config: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(
        SAEnum(LeadStatus, name="lead_status"), nullable=False, default=LeadStatus.new
    )
    source: Mapped[LeadSource] = mapped_column(
        SAEnum(LeadSource, name="lead_source"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped[Optional[Product]] = relationship()

    __table_args__ = (
        Index("idx_leads_status_created", "status", "created_at"),
        Index("idx_leads_user", "user_id"),
    )


class Faq(Base):
    __tablename__ = "faq"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("admins.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    photo_file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[BroadcastStatus] = mapped_column(
        SAEnum(BroadcastStatus, name="broadcast_status"),
        nullable=False,
        default=BroadcastStatus.draft,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
