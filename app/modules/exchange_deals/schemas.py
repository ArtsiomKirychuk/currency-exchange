from fastapi import Form, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator, computed_field
from decimal import Decimal
from datetime import datetime, date, time, timedelta

from app.modules.exchange_deals.models import ExchangeDealStatus


class ExchangeDealCreate(BaseModel):
    source_amount: Decimal = Field(gt=0)
    source_currency_abbreviation: str
    target_currency_abbreviation: str

    @classmethod
    def as_form(
        cls,
        source_amount: Decimal = Form(),
        source_abbreviation: str = Form(),
        target_abbreviation: str = Form(),
    ):
        return cls(
            source_amount=source_amount,
            source_currency_abbreviation=source_abbreviation,
            target_currency_abbreviation=target_abbreviation,
        )

class ExchangeDealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_amount: Decimal
    source_currency: str
    target_amount: Decimal
    target_currency: str
    cross_rate: Decimal
    source_rate_date: date
    target_rate_date: date
    status: ExchangeDealStatus
    created_at: datetime
    expires_at: datetime


class ExchangeDealStatistics(BaseModel):
    source_currency: str
    target_currency: str
    total_source_amount: Decimal
    total_target_amount: Decimal
    deals_count: int


class ExchangeDealStatisticsRequest(BaseModel):
    date_from: date = Field(
        description="Start date (inclusive).",
        json_schema_extra={"example": "2026-11-01"}
    )
    date_to: date = Field(
        description="End date (inclusive).",
        json_schema_extra={"example": "2026-11-05"}
    )
    currency_abbreviation: str | None = Field(
        default=None,
        description="Currency abbreviation. If omitted, statistics are returned for all currencies.",
        json_schema_extra={"example": "USD"}
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from > self.date_to:
            raise ValueError("date_from must be less than or equal to date_to")
        return self

    @computed_field
    @property
    def datetime_from(self) -> datetime:
        return datetime.combine(self.date_from, time.min)

    @computed_field
    @property
    def datetime_to(self) -> datetime:
        return datetime.combine(self.date_to + timedelta(days=1), time.min)
