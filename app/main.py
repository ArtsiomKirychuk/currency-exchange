from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from app.core.jobs import update_rates_job
from app.core.scheduler import start_scheduler, stop_scheduler
from app.modules.exchange_rates.router import router as exchange_rates_router
from app.modules.exchange_deals.router import router as exchange_deals_router
from app.modules.exchange_deals.ui_router import router as exchange_deals_ui_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_rates_job()
    await start_scheduler()
    yield
    await stop_scheduler()

app = FastAPI(lifespan=lifespan)

@app.get("/", include_in_schema=False)
async def home():
    return RedirectResponse(url="/exchange-deals", status_code=302)

@app.exception_handler(404)
async def not_found(request: Request, exc: HTTPException):
    return RedirectResponse(url="/exchange-deals", status_code=302)

app.include_router(exchange_rates_router)
app.include_router(exchange_deals_router)
app.include_router(exchange_deals_ui_router)
