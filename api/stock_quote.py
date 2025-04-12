import requests
import os
from fastapi import APIRouter, HTTPException, Query
import httpx
from api.stock_quote_tiingo import get_intraday_price_tiingo_or_yfinance

def get_daily_adjusted_close(symbol, api_key):
    """
    Gets the latest daily adjusted closing price from Alpha Vantage.

    Args:
        symbol (str): The stock symbol.
        api_key (str): Your Alpha Vantage API key.

    Returns:
        float: The latest daily adjusted closing price, or None if an error occurs.
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Error Message" in data:
            print(f"API Error: {data['Error Message']}")
            return None
        if "Note" in data:
            print(f"API Advisory: {data['Note']}")
            return None

        time_series = data.get("Time Series (Daily)")
        if not time_series:
            print(f"No daily data found for {symbol}")
            return None

        latest_timestamp = max(time_series.keys())
        latest_data = time_series[latest_timestamp]
        adjusted_close = float(latest_data["5. adjusted close"]) # Use adjusted close

        return adjusted_close

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Data Parsing Error: {e}")
        return None

async def get_stock_price_tiingo(ticker):
    """
    Gets the latest stock price from Tiingo.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        str: The latest stock price, or None if an error occurs.
    """
    api_key = os.getenv("TIINGO_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Tiingo API key not found")

    url = f'https://api.tiingo.com/tiingo/daily/{ticker}/prices'
    params = {
        'token': api_key,
        'startDate': '1970-01-01',
        'endDate': '2099-12-31'
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    if not data:
        return None

    latest_price = data[0].get("close", "N/A")

    return latest_price

async def get_intraday_price_tiingo_or_yfinance_async(ticker):
    """
    Async wrapper for get_intraday_price_tiingo_or_yfinance function.
    
    Args:
        ticker (str): The stock ticker symbol.
        
    Returns:
        tuple: (price, source, timestamp) from either Tiingo or yfinance
    """
    # Get the API key for Tiingo
    tiingo_api_key = os.getenv("TIINGO_API_KEY")
    if not tiingo_api_key:
        print("Tiingo API key not found, falling back to yfinance only")
        # Import the yfinance-specific function directly
        from api.stock_quote_tiingo import get_approximate_delayed_price_yfinance
        
        # Use 15-minute delay as default
        delay_minutes = 15
        
        # Run the yfinance function in a thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        price, timestamp = await loop.run_in_executor(
            None, 
            lambda: get_approximate_delayed_price_yfinance(ticker, delay_minutes)
        )
        
        return price, "yfinance", timestamp
    
    # Use 15-minute delay as default
    delay_minutes = 15
    
    # Run the synchronous function in a thread pool to avoid blocking
    import asyncio
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        lambda: get_intraday_price_tiingo_or_yfinance(ticker, tiingo_api_key, delay_minutes)
    )
    
    return result

router = APIRouter(
    prefix="/stock_quote",
    tags=["stock_quote"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_stock_price(ticker: str = Query(..., description="Stock ticker symbol (e.g., AAPL)")):
    try:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not found")

        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}'
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        if "Global Quote" not in data:
            print(f"Alpha Vantage API response for {ticker}: {data}")
            print(f"Global Quote not found in Alpha Vantage response, falling back to Tiingo/yfinance")
            price, source, timestamp = await get_intraday_price_tiingo_or_yfinance_async(ticker)
            if price is not None:
                latest_price = str(price)
                print(f"Successfully retrieved price from {source} at {timestamp}: ${price:.2f}")
            else:
                latest_price = "N/A"
                print(f"Failed to retrieve price from both Tiingo and yfinance")
        else:
            latest_price = data["Global Quote"].get("05. price", "N/A")
            if latest_price in [None, "N/A"]:
                print(f"Alpha Vantage returned null/N/A price for {ticker}, falling back to Tiingo/yfinance")
                price, source, timestamp = await get_intraday_price_tiingo_or_yfinance_async(ticker)
                if price is not None:
                    latest_price = str(price)
                    print(f"Successfully retrieved price from {source} at {timestamp}: ${price:.2f}")
                else:
                    latest_price = "N/A"
                    print(f"Failed to retrieve price from both Tiingo and yfinance")
        return {"ticker": ticker, "latest_price": latest_price}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error processing request for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# --- Main execution ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7171, reload=True)
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not api_key:
        print("Error: ALPHAVANTAGE_API_KEY environment variable not set.")
        exit(1)

    symbol = "MSFT"
    price = get_daily_adjusted_close(symbol, api_key)

    if price is not None:
        print(f"The latest adjusted closing price of {symbol} is: ${price:.2f}")