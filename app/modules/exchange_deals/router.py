import logging
from http import HTTPStatus
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Annotated

from app.logs.decorators import log_operation
from app.logs.models import LogOperation
from app.modules.exchange_deals.exceptions import InvalidDealStatusError
from app.modules.exchange_rates.exceptions import ExchangeRateNotFoundError
from app.modules.exchange_deals.schemas import ExchangeDealResponse, ExchangeDealCreate, ExchangeDealStatisticsRequest
from app.modules.exchange_deals.service import ExchangeDealService, get_exchange_deal_service


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/exchange-deals",
    tags=["Exchange deals API"]
)


@router.post("/", response_model=ExchangeDealResponse)
@log_operation(LogOperation.CREATE_DEAL)
async def create_deal(
    data: ExchangeDealCreate,
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    try:
        return await service.create_deal(data)
    except ExchangeRateNotFoundError as exc:
        logger.warning(exc.message)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=exc.message
        )


@router.get("/statistics")
async def get_statistics(
    request: Annotated[ExchangeDealStatisticsRequest, Query()],
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    return await service.get_deals_statistics(
        datetime_from = request.datetime_from,
        datetime_to = request.date_to,
        currency_abbreviation=request.currency_abbreviation
    )


@router.get(
    "/expired",
    response_model=list[ExchangeDealResponse],
    summary="Get expired exchange deals",
    description="Retursn all exchange deals with expired status"
)
async def get_expired_deals(
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    return await service.get_expired_deals()


@router.get(
    "/pending",
    response_model=list[ExchangeDealResponse],
    summary="Get pending exchange deals",
    description="Retursn all exchange deals with pending status"
)
async def get_pending_deals(
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    return await service.get_pending_deals()


@router.get("/{deal_id}", response_model=ExchangeDealResponse)
async def get_deal(
    deal_id: int, 
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    deal = await service.get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return deal


@router.post("/{deal_id}/confirm", response_model=ExchangeDealResponse)
@log_operation(LogOperation.CONFIRM_DEAL)
async def confirm_deal(
    deal_id: int, 
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    try:
        return await service.confirm_deal(deal_id)
    except InvalidDealStatusError as exc:
        logger.warning(exc.message)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=exc.message
        )


@router.post("/{deal_id}/reject", response_model=ExchangeDealResponse)
@log_operation(LogOperation.REJECT_DEAL)
async def reject_deal(
    deal_id: int,
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    try:
        return await service.reject_deal(deal_id)
    except InvalidDealStatusError as exc:
        logger.warning(exc.message)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=exc.message
        )
