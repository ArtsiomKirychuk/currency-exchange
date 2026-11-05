from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.jobs import update_rates_job
from app.core.config import get_settings


settings = get_settings()
scheduer = AsyncIOScheduler(timezone=settings.scheduler_timezone)


async def start_scheduler():
    scheduer.add_job(
        func=update_rates_job,
        trigger="cron",
        hour=settings.scheduler_hour,
        minute=settings.scheduler_minute,
        id="update_exchange_rates",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduer.start()


async def stop_scheduler():
    scheduer.shutdown()
