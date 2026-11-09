import asyncio
from enum import Enum
from datetime import date
from app.core.config import get_settings
from app.core.database import get_session
from app.modules.exchange_rates.models import ExchangeRateModel
from .repository import ExchangeRateRepository
from app.external.nbrb.client import NBRBClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


class Periodicity(Enum):
    DAILY = 0
    MONTHLY = 1


class ExchangeRateService:

    def __init__(self, repository: ExchangeRateRepository, nbrb_client: NBRBClient, session: AsyncSession):
        self.repository = repository
        self.nbrb_client = nbrb_client
        self.session = session

    async def update_rates(self):
        is_updated_today = await self.repository.is_updated_today()
        if is_updated_today:
            return
    
        results = await asyncio.gather(
            *(self.nbrb_client.get_exchange_rates(periodicity=period.value)
              for period in Periodicity)
        )
        rates = [rate.model_dump(by_alias=False) for rates in results for rate in rates]

        if not rates:
            return
        
        await self.repository.update_rates(rates)
        await self.session.commit()

    async def get_exchange_rates(self) -> list[ExchangeRateModel]:
        return await self.repository.get_latest_rates()


def get_exchange_rate_service(session: AsyncSession = Depends(get_session)) -> ExchangeRateService:
    settings = get_settings()
    repository = ExchangeRateRepository(session)
    nbrb_client = NBRBClient(base_url=settings.nbrb_base_url)
    return ExchangeRateService(repository=repository, nbrb_client=nbrb_client, session=session)
