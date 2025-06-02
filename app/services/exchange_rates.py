import httpx
from fastapi import HTTPException
from functools import lru_cache
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List

class ExchangeRateService:
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.supported_currencies: Dict[str, str] = {}
        self._rates_cache = {}
        self._last_update = None
        self._cache_duration = timedelta(hours=1)

    async def get_rates(self, base_currency: str) -> Dict[str, float]:
        current_time = datetime.now()
        
        # Check cache
        if (base_currency in self._rates_cache and self._last_update and 
            current_time - self._last_update < self._cache_duration):
            return self._rates_cache[base_currency]

        # Fetch new rates
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/{base_currency}")
                response.raise_for_status()
                data = response.json()
                
                self._rates_cache[base_currency] = data["rates"]
                self._last_update = current_time
                return data["rates"]
            except httpx.HTTPError as e:
                raise HTTPException(status_code=503, detail="Exchange rate service unavailable")

    async def convert(self, from_currency: str, to_currency: str, amount: float) -> float:
        rates = await self.get_rates(from_currency)
        if to_currency not in rates:
            raise HTTPException(status_code=400, detail=f"Currency {to_currency} not supported")
        
        return amount * rates[to_currency]

    async def get_supported_currencies(self) -> List[str]:
        # Get rates for USD to get all supported currencies
        rates = await self.get_rates("USD")
        return ["USD"] + list(rates.keys())

# Create a singleton instance
exchange_service = ExchangeRateService()