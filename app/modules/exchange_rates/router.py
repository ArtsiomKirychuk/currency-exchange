from fastapi import APIRouter, Depends

from .schemas import ExchangeRate
from .service import ExchangeRateService, get_exchange_rate_service


router = APIRouter(
    prefix="/exchange-rates",
    tags=["Exchange Rates"]
)


@router.get("/", response_model=list[ExchangeRate])
async def get_exchange_rates(service: ExchangeRateService = Depends(get_exchange_rate_service)):

    return await service.update_rates()
