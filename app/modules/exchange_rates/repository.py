from datetime import date
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from .models import ExchangeRateModel


class ExchangeRateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_updated_today(self) -> bool:
        query = select(exists().where(ExchangeRateModel.date == date.today()))
        result = await self.session.execute(query)
        return result.scalar()

    async def get_all(self) -> list[ExchangeRateModel]:
        result = await self.session.scalars(select(ExchangeRateModel))
        return list(result.all())

    async def update_rates(self, rates: list[dict]):
        query = insert(ExchangeRateModel).values(rates) \
            .on_conflict_do_nothing(index_elements=["currency_id", "date"])
        await self.session.execute(query)
        await self.session.commit()

