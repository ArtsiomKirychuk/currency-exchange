from datetime import datetime, timezone, timedelta, UTC
from decimal import Decimal, ROUND_HALF_UP
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.config import Settings, get_settings
from app.modules.exchange_deals.repository import ExchangeDealRepository
from app.modules.exchange_deals.schemas import (
    ExchangeDealCreate,
    ExchangeDealResponse,
    ExchangeDealStatisticsRequest
)
from app.modules.exchange_deals.models import ExchangeDealModel, ExchangeDealStatus
from app.modules.exchange_rates.repository import ExchangeRateRepository
from app.modules.exchange_rates.exceptions import ExchangeRateNotFoundError
from app.modules.exchange_deals.exceptions import ExchangeDealNotFoundError, InvalidDealStatusError, DealExpiredError


class ExchangeDealService:
    def __init__(
        self, 
        deal_repository: ExchangeDealRepository,
        rate_repository: ExchangeRateRepository,
        settings: Settings,
        session: AsyncSession
    ):
        self.deal_repository = deal_repository
        self.rate_repository = rate_repository
        self.settings = settings
        self.session = session

    async def get_deal(self, deal_id: int) -> ExchangeDealModel:
        return await self.deal_repository.get_by_id(deal_id)

    async def create_deal(self, exchange_deal: ExchangeDealCreate) -> ExchangeDealModel:
        async with self.session.begin():
            source_rate = await self.rate_repository.get_latest_rate(exchange_deal.source_currency_id)
            target_rate = await self.rate_repository.get_latest_rate(exchange_deal.target_currency_id)

            if not source_rate or not target_rate:
                raise ExchangeRateNotFoundError()
            
            normalized_source_rate = source_rate.currency_official_rate / source_rate.currency_scale
            normalized_target_rate = target_rate.currency_official_rate / target_rate.currency_scale

            cross_rate: Decimal = normalized_source_rate / normalized_target_rate
            target_amount: Decimal = exchange_deal.source_amount * cross_rate
            target_amount = target_amount.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
            expire_at = datetime.now(timezone.utc) + timedelta(minutes=self.settings.expire_deal_in_minutes)

            new_deal = ExchangeDealModel(
                source_amount=exchange_deal.source_amount,
                source_currency=source_rate.currency_abbreviation,
                target_amount=target_amount,
                target_currency=target_rate.currency_abbreviation,
                cross_rate=cross_rate,
                source_rate_date=source_rate.date,
                target_rate_date=target_rate.date,
                status=ExchangeDealStatus.PENDING,
                expires_at=expire_at
            )

            deal = await self.deal_repository.create_deal(new_deal)
        return ExchangeDealResponse.model_validate(deal)

    def _validate_pending_deal(self, deal: ExchangeDealModel) -> None:
        if deal.status != ExchangeDealStatus.PENDING:
            raise InvalidDealStatusError()
        if deal.expires_at <= datetime.now(UTC):
            raise DealExpiredError()

    async def expire_deal(self, deal: ExchangeDealModel) -> ExchangeDealModel:
        deal.status = ExchangeDealStatus.EXPIRED
        return await self.deal_repository.update_deal(deal)

    async def confirm_deal(self, deal_id: int) -> ExchangeDealModel:
        async with self.session.begin():
            deal = await self.deal_repository.get_by_id(deal_id)

            if not deal:
                raise ExchangeDealNotFoundError()

            if deal.status == ExchangeDealStatus.PENDING:
                if deal.expires_at <= datetime.now(UTC):
                    return await self.expire_deal(deal)
            
            self._validate_pending_deal(deal)

            deal.status = ExchangeDealStatus.CONFIRMED
            return await self.deal_repository.update_deal(deal)

    async def reject_deal(self, deal_id: int) -> ExchangeDealModel:
        async with self.session.begin():
            deal = await self.deal_repository.get_by_id(deal_id)

            if not deal:
                raise ExchangeDealNotFoundError()
            self._validate_pending_deal(deal)
            deal.status = ExchangeDealStatus.REJECTED
            return await self.deal_repository.update_deal(deal)

    async def get_available_currencies(self) -> list:
        return await self.rate_repository.get_latest_rates()

    async def expire_overdue_deals(self) -> int:
        return await self.deal_repository.expire_overdue_deals()

    async def get_deals_statistics(
        self, 
        datetime_from: datetime, 
        datetime_to: datetime, 
        currency_abbreviation: str | None = None
    ) -> list[ExchangeDealStatisticsRequest]:

        return await self.deal_repository.get_deal_statistics(
            datetime_from=datetime_from,
            datetime_to=datetime_to,
            currency_abbreviation=currency_abbreviation
        )

    async def get_expired_deals(self) -> list[ExchangeDealModel]:
        return await self.deal_repository.get_expired_deals()
        

def get_exchange_deal_service(session: AsyncSession = Depends(get_session)):
    return ExchangeDealService(
        deal_repository=ExchangeDealRepository(session),
        rate_repository=ExchangeRateRepository(session),
        settings=get_settings(),
        session=session
    )
