from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, Date, UniqueConstraint
from decimal import Decimal
from datetime import date
from app.core.database import Base


class ExchangeRateModel(Base):
    __tablename__ = "exchange_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    currency_id: Mapped[int] = mapped_column(nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    currency_code: Mapped[int]
    currency_abbreviation: Mapped[str]
    currency_scale: Mapped[int]
    currency_name: Mapped[str]
    currency_official_rate: Mapped[Decimal] = mapped_column(Numeric(12, 6))

    __table_args__ = (
        UniqueConstraint("currency_id", "date"),
    )

