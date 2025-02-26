# AWS Simple Currency Converter

A simple currency converter using AWS services.

## Architecture
- Lambda functions for processing currency conversion requests
- External API for getting exchange rates from a third party service and getting the list of supported currencies
- External API for getting the list of countries name

## Prerequisites
- AWS CLI configured
- Python 3.x

## Setup
1. Create virtual environment:
```
python -m venv .venv
source .venv/bin/activate
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Deploy the infrastructure:
```
$ pip install -t dependencies -r requirements.txt
$ (cd dependencies; zip ../aws_lambda_artifact.zip -r .)
$ zip aws_lambda_artifact.zip -u main.py
```
4. Upload the artifact to AWS Lambda

## Usage
1. Hit the API endpoint with the following parameters:
- `from_currency`: The source currency code
- `to_currency`: The target currency code
- `amount`: The amount to convert

Example:
```
curl -X GET 'your-api-endpoint/convert?from_currency=USD&to_currency=IDR&amount=1'

```
Response:
```
{
    "from_currency":"USD",
    "to_currency":"IDR",
    "amount":1.0,
    "exchange_rate":16345.0,
    "converted_amount":16345.0,
    "datetime":"2025-02-26T00:21:00.262788",
    "countries":["Indonesia"]
}
```