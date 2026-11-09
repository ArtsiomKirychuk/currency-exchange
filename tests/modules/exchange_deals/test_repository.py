import pytest
from decimal import Decimal
from datetime import datetime, UTC, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.exchange_deals.repository import ExchangeDealRepository
from app.modules.exchange_deals.models import ExchangeDealStatus
from .helpers import make_deal


@pytest.mark.asyncio
async def test_create_deal(session: AsyncSession):
    repository = ExchangeDealRepository(session)
    deal = make_deal()

    result = await repository.create_deal(deal)

    assert result.id is not None
    assert result.source_currency == "USD"
    assert result.target_currency == "EUR"
    assert result.status == ExchangeDealStatus.PENDING


@pytest.mark.asyncio
async def test_update_deal(session: AsyncSession):
    repository = ExchangeDealRepository(session)
    deal = make_deal()

    await repository.create_deal(deal)

    deal.status = ExchangeDealStatus.CONFIRMED
    result = await repository.update_deal(deal)

    assert result is not None
    assert result.status == ExchangeDealStatus.CONFIRMED


@pytest.mark.asyncio
async def test_update_deal_not_found(session: AsyncSession):
    repository = ExchangeDealRepository(session)
    deal = make_deal()
    deal.id = int(9999)

    result = await repository.update_deal(deal)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_id(session: AsyncSession):
    repository = ExchangeDealRepository(session)
    deal = make_deal()

    await repository.create_deal(deal)

    result = await repository.get_by_id(deal.id)

    assert result is not None
    assert result.id == deal.id


@pytest.mark.asyncio
async def test_get_by_id_not_found(session: AsyncSession):
    repository = ExchangeDealRepository(session)

    result = await repository.get_by_id(int(9999))

    assert result is None


@pytest.mark.asyncio
async def test_expire_overdue_deals(session: AsyncSession):
    repository = ExchangeDealRepository(session)
    now = datetime.now(UTC)

    overdue_pending = make_deal(
        expires_at=now - timedelta(minutes=5),
    )
    active_pending = make_deal(
        expires_at=now + timedelta(minutes=5),
    )
    overdue_confirmed = make_deal(
        status=ExchangeDealStatus.CONFIRMED,
        expires_at=now - timedelta(minutes=5),
    )

    session.add_all([
        overdue_pending,
        active_pending,
        overdue_confirmed,
    ])
    await session.flush()

    result = await repository.expire_overdue_deals()

    assert result == 1

    assert overdue_pending.status == ExchangeDealStatus.EXPIRED
    assert active_pending.status == ExchangeDealStatus.PENDING
    assert overdue_confirmed.status == ExchangeDealStatus.CONFIRMED


@pytest.mark.asyncio
async def test_get_deal_statistics(session: AsyncSession):
    repository = ExchangeDealRepository(session)

    datetime_from = datetime(2026, 11, 1, tzinfo=UTC)
    datetime_to = datetime(2026, 11, 10, tzinfo=UTC)

    deals = [
        make_deal(
            source_currency="USD",
            target_currency="EUR",
            source_amount=Decimal("100"),
            target_amount=Decimal("90"),
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 11, 3, tzinfo=UTC),
        ),
        make_deal(
            source_currency="USD",
            target_currency="EUR",
            source_amount=Decimal("200"),
            target_amount=Decimal("180"),
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 11, 4, tzinfo=UTC),
        ),
        make_deal(
            source_currency="USD",
            target_currency="BYN",
            source_amount=Decimal("50"),
            target_amount=Decimal("150"),
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 11, 5, tzinfo=UTC),
        ),
        make_deal(
            source_currency="USD",
            target_currency="EUR",
            status=ExchangeDealStatus.PENDING,
            created_at=datetime(2026, 11, 5, tzinfo=UTC),
        ),
        make_deal(
            source_currency="EUR",
            target_currency="USD",
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 10, 31, tzinfo=UTC),
        ),
    ]

    session.add_all(deals)
    await session.flush()

    result = await repository.get_deal_statistics(
        datetime_from,
        datetime_to,
    )

    assert len(result) == 2

    eur_stats = next(
        item for item in result
        if item["target_currency"] == "EUR"
    )

    assert eur_stats["source_currency"] == "USD"
    assert eur_stats["total_source_amount"] == Decimal("300")
    assert eur_stats["total_target_amount"] == Decimal("270")
    assert eur_stats["deals_count"] == 2


@pytest.mark.asyncio
async def test_get_deal_statistics_by_currency(session: AsyncSession):
    repository = ExchangeDealRepository(session)

    datetime_from = datetime(2026, 11, 1, tzinfo=UTC)
    datetime_to = datetime(2026, 11, 10, tzinfo=UTC)

    session.add_all([
        make_deal(
            source_currency="USD",
            target_currency="EUR",
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 11, 3, tzinfo=UTC),
        ),
        make_deal(
            source_currency="EUR",
            target_currency="USD",
            status=ExchangeDealStatus.CONFIRMED,
            created_at=datetime(2026, 11, 3, tzinfo=UTC),
        ),
    ])
    await session.flush()

    result = await repository.get_deal_statistics(
        datetime_from,
        datetime_to,
        currency_abbreviation="USD",
    )

    assert len(result) == 1
    assert result[0]["source_currency"] == "USD"
    assert result[0]["target_currency"] == "EUR"


@pytest.mark.asyncio
async def test_get_expired_deals(session: AsyncSession):
    repository = ExchangeDealRepository(session)

    older_deal = make_deal(
        status=ExchangeDealStatus.EXPIRED,
        created_at=datetime(2026, 11, 1, tzinfo=UTC),
    )
    newer_deal = make_deal(
        status=ExchangeDealStatus.EXPIRED,
        created_at=datetime(2026, 11, 5, tzinfo=UTC),
    )
    pending_deal = make_deal(
        status=ExchangeDealStatus.PENDING,
        created_at=datetime(2026, 11, 6, tzinfo=UTC),
    )

    session.add_all([older_deal, newer_deal, pending_deal])
    await session.flush()

    result = await repository.get_expired_deals()

    assert len(result) == 2
    assert result[0].id == newer_deal.id
    assert result[1].id == older_deal.id