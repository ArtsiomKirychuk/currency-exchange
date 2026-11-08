from datetime import datetime, UTC
from sqlalchemy import update, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.exchange_deals.models import ExchangeDealModel, ExchangeDealStatus


class ExchangeDealRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deal(self, deal: ExchangeDealModel) -> ExchangeDealModel:
        self.session.add(deal)
        await self.session.flush()
        return deal

    async def update_deal(self, deal: ExchangeDealModel) -> ExchangeDealModel | None:
        query = update(ExchangeDealModel) \
            .where(ExchangeDealModel.id == deal.id) \
            .values(status=deal.status) \
            .returning(ExchangeDealModel)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, deal_id: int) -> ExchangeDealModel:
        return await self.session.get(ExchangeDealModel, deal_id)

    async def expire_overdue_deals(self) -> int:
        query = update(ExchangeDealModel) \
            .where(
                ExchangeDealModel.status == ExchangeDealStatus.PENDING,
                ExchangeDealModel.expires_at <= datetime.now(UTC)
            ) \
            .values(status=ExchangeDealStatus.EXPIRED)

        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount

    async def get_deal_statistics(
            self,
            datetime_from: datetime,
            datetime_to: datetime,
            currency_abbreviation: str | None = None
    ):
        query = select(
            ExchangeDealModel.source_currency,
            ExchangeDealModel.target_currency,
            func.sum(ExchangeDealModel.source_amount).label("total_source_amount"),
            func.sum(ExchangeDealModel.target_amount).label("total_target_amount"),
            func.count(ExchangeDealModel.id).label("deals_count")
        ).where(
            ExchangeDealModel.created_at >= datetime_from,
            ExchangeDealModel.created_at < datetime_to,
            ExchangeDealModel.status == ExchangeDealStatus.CONFIRMED
        )

        if currency_abbreviation:
            query = query.where(ExchangeDealModel.source_currency==currency_abbreviation)

        query = query.group_by(ExchangeDealModel.source_currency, ExchangeDealModel.target_currency)
        result = await self.session.execute(query)
        return result.mappings().all()

    async def get_expired_deals(self) -> list[ExchangeDealModel]:
        query = select(ExchangeDealModel) \
            .where(ExchangeDealModel.status==ExchangeDealStatus.EXPIRED) \
            .order_by(ExchangeDealModel.created_at.desc())

        result = await self.session.execute(query)
        return result.scalars().all()
