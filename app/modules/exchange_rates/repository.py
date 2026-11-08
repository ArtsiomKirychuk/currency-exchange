from datetime import date
from sqlalchemy import select, exists, func
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

    async def get_latest_rates(self) -> list[ExchangeRateModel]:
        ranked_rates = (
            select(
                ExchangeRateModel,
                func.row_number()
                .over(
                    partition_by=ExchangeRateModel.currency_id,
                    order_by=ExchangeRateModel.date.desc(),
                )
                .label("row_num"),
            )
            .subquery()
        )

        query = (
            select(ExchangeRateModel)
            .join(
                ranked_rates,
                ExchangeRateModel.id == ranked_rates.c.id,
            )
            .where(ranked_rates.c.row_num == 1)
            .order_by(ExchangeRateModel.date.desc())
        )

        result = await self.session.scalars(query)
        return result.all()

    async def update_rates(self, rates: list[dict]):
        query = insert(ExchangeRateModel).values(rates) \
            .on_conflict_do_nothing(index_elements=["currency_id", "date"])
        await self.session.execute(query)
        await self.session.commit()

    async def get_latest_rate(self, currency_id: int) -> ExchangeRateModel | None:
        query = select(ExchangeRateModel) \
            .where(ExchangeRateModel.currency_id==currency_id) \
            .order_by(ExchangeRateModel.date.desc())\
            .limit(1)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

