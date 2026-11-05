from httpx2 import AsyncClient
from typing import Literal

from app.modules.exchange_rates.schemas import NBRBExchangeRate


class NBRBClient:

    def __init__(self, base_url: str):
        self.base_url = base_url

    async def get_exchange_rates(self, periodicity: Literal[0,1]) -> list[NBRBExchangeRate]:
        async with AsyncClient(base_url=self.base_url) as client:

            response = await client.get(
                url="/exrates/rates",
                params={"periodicity": periodicity}
            )

            response.raise_for_status()

            return [NBRBExchangeRate.model_validate(item) for item in response.json()]
