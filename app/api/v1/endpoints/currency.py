from fastapi import APIRouter, Depends
from app.models.currency import (
    CurrencyConversionRequest,
    CurrencyConversionResponse,
    SupportedCurrenciesResponse
)
from app.services.exchange_rates import exchange_service
from decimal import Decimal
from fastapi import HTTPException, Request
import time
from typing import Dict, List

router = APIRouter()

# Simple in-memory rate limiting
rate_limits: Dict[str, List[float]] = {}
RATE_LIMIT = 100  # requests per minute
RATE_WINDOW = 60  # seconds

def check_rate_limit(request: Request):
    client_ip = request.client.host
    now = time.time()
    
    if client_ip not in rate_limits:
        rate_limits[client_ip] = []
    
    # Remove old timestamps
    rate_limits[client_ip] = [t for t in rate_limits[client_ip] if now - t < RATE_WINDOW]
    
    if len(rate_limits[client_ip]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    rate_limits[client_ip].append(now)

@router.get("/currencies", response_model=SupportedCurrenciesResponse)
async def get_currencies(request: Request):
    check_rate_limit(request)
    currencies = await exchange_service.get_supported_currencies()
    return SupportedCurrenciesResponse(currencies=currencies)

@router.post("/convert", response_model=CurrencyConversionResponse)
async def convert_currency(
    conversion: CurrencyConversionRequest,
    request: Request
):
    check_rate_limit(request)
    
    # Convert the amount
    converted_amount = await exchange_service.convert(
        conversion.from_currency,
        conversion.to_currency,
        float(conversion.amount)
    )
    
    # Get the exchange rate
    rates = await exchange_service.get_rates(conversion.from_currency)
    exchange_rate = rates[conversion.to_currency]
    
    return CurrencyConversionResponse(
        from_currency=conversion.from_currency,
        to_currency=conversion.to_currency,
        amount=conversion.amount,
        converted_amount=Decimal(str(converted_amount)),
        exchange_rate=Decimal(str(exchange_rate))
    )