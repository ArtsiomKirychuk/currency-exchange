from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.exchange_deals.models import (
    ExchangeDealModel,
    ExchangeDealStatus,
)
from app.modules.exchange_deals.repository import ExchangeDealRepository


def make_deal(
    source_currency="USD",
    target_currency="EUR",
    source_amount=Decimal("100"),
    target_amount=Decimal("90"),
    status=ExchangeDealStatus.PENDING,
    created_at=None,
    expires_at=None,
):
    now = datetime.now(UTC)

    return ExchangeDealModel(
        source_currency=source_currency,
        target_currency=target_currency,
        source_amount=source_amount,
        target_amount=target_amount,
        cross_rate=Decimal("0.9"),
        source_rate_date=date.today(),
        target_rate_date=date.today(),
        status=status,
        created_at=created_at or now,
        expires_at=expires_at or now + timedelta(minutes=10),
    )