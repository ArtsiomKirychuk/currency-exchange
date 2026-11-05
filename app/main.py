from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.external.nbrb.client import NBRBClient
from app.core.jobs import update_rates_job
from app.core.scheduler import start_scheduler, stop_scheduler
from app.modules.exchange_rates.router import router as exchange_rates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_rates_job()
    await start_scheduler()
    yield
    await stop_scheduler()

app = FastAPI(lifespan=lifespan)
app.include_router(exchange_rates_router)
