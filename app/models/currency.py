from pydantic import BaseModel, Field
from decimal import Decimal

class CurrencyConversion(BaseModel):
    from_currency: str = Field(..., min_length=3, max_length=3, description="Three-letter currency code to convert from")
    to_currency: str = Field(..., min_length=3, max_length=3, description="Three-letter currency code to convert to")
    amount: Decimal = Field(..., gt=0, description="Amount to convert")