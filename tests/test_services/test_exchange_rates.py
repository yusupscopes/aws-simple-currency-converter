import pytest
from app.services.exchange_rates import ExchangeRateService
from fastapi import HTTPException
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

@pytest.fixture
async def exchange_service():
    return ExchangeRateService()

@pytest.mark.asyncio
async def test_get_rates_success(exchange_service):
    service = await exchange_service
    mock_response = {
        "rates": {
            "EUR": 0.85,
            "GBP": 0.73,
            "USD": 1.0
        }
    }
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            raise_for_status=AsyncMock(),
            json=AsyncMock(return_value=mock_response)
        )
        
        rates = await service.get_rates("USD")
        assert rates["EUR"] == 0.85
        assert rates["GBP"] == 0.73
        
        # Test caching
        cached_rates = await service.get_rates("USD")
        assert cached_rates == rates
        mock_get.assert_called_once()  # Ensure API was only called once

@pytest.mark.asyncio
async def test_get_rates_cache_expiration(exchange_service):
    service = await exchange_service
    mock_response = {"rates": {"EUR": 0.85}}
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            status_code=200,
            raise_for_status=AsyncMock(),
            json=AsyncMock(return_value=mock_response)
        )
        
        # First call
        await service.get_rates("USD")
        
        # Simulate cache expiration
        service._last_update = datetime.now() - timedelta(hours=2)
        
        # Second call should trigger new API request
        await service.get_rates("USD")
        assert mock_get.call_count == 2

@pytest.mark.asyncio
async def test_get_rates_api_error(exchange_service):
    service = await exchange_service
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = httpx.HTTPError("API Error")
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_rates("USD")
        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Exchange rate service unavailable"

@pytest.mark.asyncio
async def test_convert_success(exchange_service):
    service = await exchange_service
    with patch.object(service, "get_rates") as mock_get_rates:
        mock_get_rates.return_value = {"EUR": 0.85}
        result = await service.convert("USD", "EUR", 100.0)
        assert result == 85.0

@pytest.mark.asyncio
async def test_convert_unsupported_currency(exchange_service):
    service = await exchange_service
    with patch.object(service, "get_rates") as mock_get_rates:
        mock_get_rates.return_value = {"EUR": 0.85}
        with pytest.raises(HTTPException) as exc_info:
            await service.convert("USD", "XXX", 100.0)
        assert exc_info.value.status_code == 400
        assert "Currency XXX not supported" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_supported_currencies(exchange_service):
    service = await exchange_service
    with patch.object(service, "get_rates") as mock_get_rates:
        mock_get_rates.return_value = {"EUR": 0.85, "GBP": 0.73}
        currencies = await service.get_supported_currencies()
        assert set(currencies) == {"USD", "EUR", "GBP"}