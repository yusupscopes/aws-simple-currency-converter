from fastapi import FastAPI, HTTPException
from mangum import Mangum
import httpx
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
handler = Mangum(app)

@app.get("/")
async def hello():
    return {"message": "Hello from currency converter"}

async def get_exchange_rates(from_currency: str) -> dict:
    api_key = os.getenv("CURRENCY_FREAKS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}&base={from_currency}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching exchange rates: {str(e)}")

async def get_countries(to_currency: str) -> list[str]:
    url = f"https://restcountries.com/v3.1/currency/{to_currency}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            # Extract just the common names of countries from the response
            countries = [country["name"]["common"] for country in response.json()]
            return countries
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")

@app.get("/convert")
async def convert_currency(from_currency: str, to_currency: str, amount: Optional[float] = 1.0):
    try:
        rates_data = await get_exchange_rates(from_currency)
        countries = await get_countries(to_currency)
        
        if 'rates' not in rates_data:
            raise HTTPException(status_code=400, detail="Invalid response from exchange rate API")
        
        if to_currency not in rates_data['rates']:
            raise HTTPException(status_code=400, detail=f"Currency {to_currency} not found")
        
        exchange_rate = float(rates_data['rates'][to_currency])
        converted_amount = amount * exchange_rate
        
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "amount": amount,
            "exchange_rate": exchange_rate,
            "converted_amount": converted_amount,
            "datetime": datetime.now().isoformat(),
            "countries": countries
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid currency or amount")