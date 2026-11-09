import logging

from app.core.config import get_settings
from app.core.database import async_session_factory
from app.modules.exchange_rates.service import ExchangeRateService
from app.modules.exchange_rates.repository import ExchangeRateRepository
from app.modules.exchange_deals.service import ExchangeDealService
from app.modules.exchange_deals.repository import ExchangeDealRepository
from app.external.nbrb.client import NBRBClient


logger = logging.getLogger(__name__)


async def update_rates_job():
    logger.info("Starting exchange rates update job.")

    settings = get_settings()
    async with async_session_factory() as session:
        repository = ExchangeRateRepository(session=session)
        nbrb_client = NBRBClient(base_url=settings.nbrb_base_url)

        service = ExchangeRateService(repository=repository, nbrb_client=nbrb_client, session=session)
        await service.update_rates()

async def expire_overdue_deals_job():
    settings = get_settings()

    async with async_session_factory() as session:
        logger.info("Starting overdue deals expiration job.")
        deal_repository = ExchangeDealRepository(session)
        rate_repository = ExchangeRateRepository(session)
        service = ExchangeDealService(
            deal_repository=deal_repository,
            rate_repository=rate_repository,
            settings=settings,
            session=session
        )

        expired_deals_amount = await service.expire_overdue_deals()
        logger.info(f"NUM DEALS WAS EXPIRED: {expired_deals_amount}")
