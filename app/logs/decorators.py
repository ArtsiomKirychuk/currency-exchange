from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession

from app.logs.models import LogModel, LogOperation
from app.core.database import async_session_factory


def log_operation(operation: LogOperation):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            async with async_session_factory() as session:
                async with session.begin():
                    log = LogModel(operation=operation)
                    session.add(log)

            return result
        return wrapper
    return decorator