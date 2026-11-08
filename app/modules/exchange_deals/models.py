from enum import Enum
from datetime import date, datetime
from sqlalchemy import (Numeric, Date, DateTime, String, func, Enum as SQLAlchemyEnum)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from app.core.database import Base


class ExchangeDealStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ExchangeDealModel(Base):
    __tablename__ = "exchange_deals"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    cross_rate: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    source_rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_rate_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ExchangeDealStatus] = mapped_column(
        SQLAlchemyEnum(ExchangeDealStatus, name="exchange_deal_status"),
        default=ExchangeDealStatus.PENDING,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
