import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.exchange_rates import ExchangeRateService
from unittest.mock import AsyncMock

[pytest]
asyncio_mode = "auto"

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_exchange_service(monkeypatch):
    mock_service = AsyncMock(spec=ExchangeRateService)
    
    # Mock common responses
    mock_service.get_supported_currencies.return_value = ["USD", "EUR", "GBP"]
    mock_service.get_rates.return_value = {
        "EUR": 0.85,
        "GBP": 0.73,
        "USD": 1.0
    }
    mock_service.convert.return_value = 85.0  # Example for 100 USD to EUR
    
    monkeypatch.setattr("app.api.v1.endpoints.currency.exchange_service", mock_service)
    return mock_service