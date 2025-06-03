import pytest
from decimal import Decimal

def test_get_currencies(test_client, mock_exchange_service):
    response = test_client.get("/api/v1/currency/currencies")
    assert response.status_code == 200
    assert response.json() == {"currencies": ["USD", "EUR", "GBP"]}

def test_convert_currency(test_client, mock_exchange_service):
    test_data = {
        "from_currency": "USD",
        "to_currency": "EUR",
        "amount": "100.00"
    }
    
    response = test_client.post("/api/v1/currency/convert", json=test_data)
    assert response.status_code == 200
    
    result = response.json()
    assert result["from_currency"] == "USD"
    assert result["to_currency"] == "EUR"
    assert Decimal(result["converted_amount"]) == Decimal("85.0")
    assert Decimal(result["exchange_rate"]) == Decimal("0.85")

def test_rate_limiting(test_client, mock_exchange_service):
    # Make multiple requests to trigger rate limit
    for _ in range(101):  # One more than the limit
        response = test_client.get("/api/v1/currency/currencies")
    
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"]