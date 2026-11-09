import pytest
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import delete
from app.modules.exchange_rates.repository import ExchangeRateRepository
from app.modules.exchange_rates.models import ExchangeRateModel


@pytest.mark.asyncio
async def test_get_latest_rate(session):
    repository = ExchangeRateRepository(session)

    rate = ExchangeRateModel(
        currency_id=431,
        currency_code=840,
        date=date(2026, 11, 5),
        currency_abbreviation="USD",
        currency_scale=1,
        currency_name="Доллар США",
        currency_official_rate=Decimal("2.991500")        
    )

    session.add(rate)
    await session.commit()

    result = await repository.get_latest_rate(currency_id=rate.currency_id)

    assert result is not None
    assert result.currency_abbreviation == "USD"
    assert result.currency_official_rate == Decimal("2.991500")


def make_rate(
    currency_id: int,
    rate_date: date,
    official_rate: Decimal = Decimal("3.500000"),
) -> ExchangeRateModel:
    return ExchangeRateModel(
        currency_id=currency_id,
        date=rate_date,
        currency_code=840,
        currency_abbreviation="USD",
        currency_scale=1,
        currency_name="US Dollar",
        currency_official_rate=official_rate,
    )


@pytest.mark.asyncio
async def test_is_updated_today(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    session.add(make_rate(431, date.today()))
    await session.flush()

    assert await repository.is_updated_today() is True


@pytest.mark.asyncio
async def test_is_not_updated_today(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    session.add(make_rate(431, date.today() - timedelta(days=1)))
    await session.flush()

    assert await repository.is_updated_today() is False


@pytest.mark.asyncio
async def test_get_all(session: AsyncSession):
    repository = ExchangeRateRepository(session)
    session.execute(delete(ExchangeRateModel))
    rates = [
        make_rate(431, date.today()),
        make_rate(451, date.today()),
    ]

    session.add_all(rates)
    await session.flush()

    result = await repository.get_all()

    assert len(result) == 2
    assert {rate.currency_id for rate in result} == {431, 451}


@pytest.mark.asyncio
async def test_get_latest_rates(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    today = date.today()

    session.add_all([
        make_rate(431, today - timedelta(days=2), Decimal("3.40")),
        make_rate(431, today, Decimal("3.50")),
        make_rate(451, today - timedelta(days=1), Decimal("2.90")),
        make_rate(451, today, Decimal("3.00")),
    ])
    await session.flush()

    result = await repository.get_latest_rates()

    assert len(result) == 2

    rates = {rate.currency_id: rate for rate in result}

    assert rates[431].currency_official_rate == Decimal("3.50")
    assert rates[451].currency_official_rate == Decimal("3.00")


@pytest.mark.asyncio
async def test_get_latest_rate(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    today = date.today()

    session.add_all([
        make_rate(431, today - timedelta(days=1), Decimal("3.40")),
        make_rate(431, today, Decimal("3.50")),
    ])
    await session.flush()

    result = await repository.get_latest_rate(431)

    assert result is not None
    assert result.currency_id == 431
    assert result.date == today
    assert result.currency_official_rate == Decimal("3.50")


@pytest.mark.asyncio
async def test_get_latest_rate_not_found(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    result = await repository.get_latest_rate(999)

    assert result is None


@pytest.mark.asyncio
async def test_update_rates(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    rates = [
        {
            "currency_id": 431,
            "date": date.today(),
            "currency_code": 840,
            "currency_abbreviation": "USD",
            "currency_scale": 1,
            "currency_name": "US Dollar",
            "currency_official_rate": Decimal("3.50"),
        },
        {
            "currency_id": 451,
            "date": date.today(),
            "currency_code": 978,
            "currency_abbreviation": "EUR",
            "currency_scale": 1,
            "currency_name": "Euro",
            "currency_official_rate": Decimal("3.80"),
        },
    ]

    await repository.update_rates(rates)

    result = await repository.get_all()

    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_rates_ignores_duplicates(session: AsyncSession):
    repository = ExchangeRateRepository(session)

    rate = {
        "currency_id": 431,
        "date": date.today(),
        "currency_code": 840,
        "currency_abbreviation": "USD",
        "currency_scale": 1,
        "currency_name": "US Dollar",
        "currency_official_rate": Decimal("3.50"),
    }

    await repository.update_rates([rate])
    await repository.update_rates([rate])

    result = await repository.get_all()

    assert len(result) == 1
