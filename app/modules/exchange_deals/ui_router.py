from pathlib import Path
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated

from app.logs.decorators import log_operation
from app.logs.models import LogOperation
from app.modules.exchange_deals.schemas import ExchangeDealResponse, ExchangeDealCreate, ExchangeDealStatisticsRequest
from app.modules.exchange_deals.service import ExchangeDealService, get_exchange_deal_service


router = APIRouter(
    prefix="/exchange-deals",
    tags=["Exchange Deals UI HTMLResponse"]
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def create_deal_page(
    request: Request, 
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    currencies = await service.get_available_currencies()
    return templates.TemplateResponse(
        request=request,
        name="create_deal.html",
        context={"currencies": currencies}
    )

@router.post("/", response_model=ExchangeDealResponse)
@log_operation(LogOperation.CREATE_DEAL)
async def create_deal(
    data: ExchangeDealCreate = Depends(ExchangeDealCreate.as_form),
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    deal = await service.create_deal(data)

    return RedirectResponse(
        url=f"/exchange-deals/{deal.id}",
        status_code=303,
    )


@router.get("/{deal_id}", response_class=HTMLResponse)
async def get_deal(
    request: Request,
    deal_id: int, 
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    deal = await service.get_deal(deal_id)

    if not deal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

    return templates.TemplateResponse(
        request=request,
        name="deal.html",
        context={"deal": deal}
    )


@router.post("/{deal_id}/confirm", response_class=HTMLResponse)
@log_operation(LogOperation.CONFIRM_DEAL)
async def confirm_deal(
    request: Request,
    deal_id: int, 
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):

    deal = await service.confirm_deal(deal_id)

    return templates.TemplateResponse(
        request=request,
        name="deal.html",
        context={"deal": deal}
    )

@router.post("/{deal_id}/reject", response_class=HTMLResponse)
@log_operation(LogOperation.REJECT_DEAL)
async def reject_deal(
    request: Request,
    deal_id: int,
    service: ExchangeDealService = Depends(get_exchange_deal_service)
):
    deal = await service.reject_deal(deal_id)
    return templates.TemplateResponse(
        request=request,
        name="deal.html",
        context={"deal": deal}
    )
