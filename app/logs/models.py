from enum import Enum
from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLAlchemyEnum, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LogOperation(str, Enum):
    CREATE_DEAL = "CREATE_DEAL"
    CONFIRM_DEAL = "CONFIRM_DEAL"
    REJECT_DEAL = "REJECT_DEAL"
    UPDATE_EXCHANGE_RATES = "UPDATE_EXCHANGE_RATES"


class LogModel(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    operation: Mapped[LogOperation] = mapped_column(
        SQLAlchemyEnum(LogOperation),
        nullable=False,
    )
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )