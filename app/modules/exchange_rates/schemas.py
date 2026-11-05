import datetime
import decimal
from pydantic import BaseModel, ConfigDict, Field


class ExchangeRate(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )

    currency_id: int
    currency_code: int
    date: datetime.date
    currency_abbreviation: str
    currency_scale: int
    currency_name: str
    currency_official_rate: decimal.Decimal


class NBRBExchangeRate(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        validate_by_alias=True, 
        extra="ignore"
    )

    currency_id: int = Field(alias="Cur_ID")
    currency_code: int = Field(alias="Cur_Code")
    date: datetime.date = Field(alias="Date")
    currency_abbreviation: str = Field(alias="Cur_Abbreviation")
    currency_scale: int = Field(alias="Cur_Scale")
    currency_name: str = Field(alias="Cur_Name")
    currency_official_rate: decimal.Decimal = Field(alias="Cur_OfficialRate")
