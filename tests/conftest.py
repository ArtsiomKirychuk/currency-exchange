import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import delete, text
from sqlalchemy.pool import NullPool


from app.core.config import get_settings
from app.modules.exchange_rates.models import ExchangeRateModel


settings = get_settings()


engine = create_async_engine(
    settings.build_db_url,
    poolclass=NullPool,
)

async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

@pytest_asyncio.fixture
async def session():
    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def clean_db(session):
    await session.execute(text("""
        TRUNCATE TABLE exchange_deals, exchange_rates
        RESTART IDENTITY CASCADE
    """))
    await session.commit()
