from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List

class CurrencyConversionRequest(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3, description="Three-letter currency code to convert from")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Three-letter currency code to convert to")
    amount: Decimal = Field(..., gt=0, description="Amount to convert")

class CurrencyConversionResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal
    converted_amount: Decimal
    exchange_rate: Decimal

class SupportedCurrenciesResponse(BaseModel):
    currencies: List[str]