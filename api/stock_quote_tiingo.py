import requests
import os
from datetime import datetime, timedelta
import httpx
from fastapi import HTTPException
import yfinance as yf  # Import yfinance
import pytz
import time

def get_intraday_price_tiingo_or_yfinance(symbol, tiingo_api_key, delay_minutes=15):
    """
    Gets an approximate intraday delayed stock price, trying Tiingo first,
    then yfinance if Tiingo fails.  Prioritizes minimizing delay.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL").
        tiingo_api_key (str): Your Tiingo API key.
        delay_minutes (int): Target delay in minutes.

    Returns:
        float: The approximate delayed intraday price, or None if both fail.
        str: The source ("Tiingo" or "yfinance"), or None.
        str: The timestamp of the price, or None.
    """

    # --- Try Tiingo first (IEX Real-Time) ---
    price, timestamp = get_delayed_price_tiingo_intraday(symbol, tiingo_api_key, delay_minutes)
    if price is not None:
        return price, "Tiingo", timestamp

    print("Tiingo IEX Real-Time failed, trying yfinance...")

    # --- Try yfinance if Tiingo fails ---
    price, timestamp = get_approximate_delayed_price_yfinance(symbol, delay_minutes)
    if price is not None:
        return price, "yfinance", timestamp

    print("Both Tiingo and yfinance failed.")
    return None, None, None



def get_delayed_price_tiingo_intraday(symbol, api_key, delay_minutes):
    """
    Gets delayed intraday price from Tiingo using IEX Real-time (if available).

    Tiingo's *free* tier usually has only end-of-day data for IEX.  However,
    some accounts *might* have access to IEX real-time data, even on the free
    tier. This function attempts to use that endpoint.  If you *know* you
    don't have IEX real-time, you can skip this function.

    Args:
        symbol (str): The stock symbol.
        api_key (str): Your Tiingo API Key
        delay_minutes (int): The target delay. Not directly used by this function,
            but included for consistency with the yfinance function.

    Returns:
        float:  The price, or None on error.
        str: The timestamp, or None on error.
    """
    url = f"https://api.tiingo.com/iex/?tickers={symbol}&token={api_key}"

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            print(f"No IEX Real-time data found for {symbol} on Tiingo")
            return None, None
        
        # We expect a list, even for a single ticker.
        if not isinstance(data, list) or len(data) == 0:
            print(f"Unexpected response format from Tiingo IEX: {data}")
            return None, None

        price_data = data[0]  # Get the first (and likely only) item

        # Check for error indicators in the response
        if "ticker" not in price_data or price_data["ticker"].lower() != symbol.lower():
            print(f"Tiingo IEX returned data for an unexpected ticker: {price_data.get('ticker')}")
            return None, None
        if "last" not in price_data:
            print(f"No 'last' price found in Tiingo IEX response for {symbol}")
            return None, None

        price = float(price_data["last"])  # Use the "last" price (most recent)
        timestamp = price_data["timestamp"]  # Tiingo provides a timestamp

        return price, timestamp
    
    except requests.exceptions.RequestException as e:
        print(f"Tiingo IEX Request Error: {e}")
        return None, None
    except (KeyError, ValueError, TypeError) as e:
        print(f"Tiingo IEX Data Parsing Error: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred with Tiingo IEX: {e}")
        return None, None



def get_approximate_delayed_price_yfinance(symbol, delay_minutes=15):
    """
    Gets an approximate 15-minute delayed stock price using yfinance.

    This function uses yfinance's 1-minute intraday data.  Because yfinance
    data isn't perfectly real-time, this is an *approximation*.  The function
    waits until at least `delay_minutes` have passed since the market opened
    before fetching data, to increase the likelihood of getting data that's
    at least somewhat delayed.

    Args:
        symbol (str): The stock symbol (e.g., "AAPL").
        delay_minutes (int): The desired delay in minutes.

    Returns:
        float: The approximate delayed price, or None if an error occurs.
        str: The timestamp of the retrieved price, or None.
    """
    try:
        # 1. Get the current time in Eastern Time (US market time)
        eastern = pytz.timezone('US/Eastern')
        now_eastern = datetime.now(eastern)

        # 2. Calculate market open time (9:30 AM Eastern)
        market_open = now_eastern.replace(hour=9, minute=30, second=0, microsecond=0)

        # 3. Calculate the target time (current time - delay)
        target_time = now_eastern - timedelta(minutes=delay_minutes)

        # 4. Wait until at least the delay has passed since market open.
        if now_eastern < market_open + timedelta(minutes=delay_minutes):
            wait_seconds = (market_open + timedelta(minutes=delay_minutes) - now_eastern).total_seconds()
            print(f"Waiting {wait_seconds:.0f} seconds for market data to become available...")
            time.sleep(wait_seconds)
            # Recalculate target time after waiting.
            now_eastern = datetime.now(eastern)
            target_time = now_eastern - timedelta(minutes=delay_minutes)


        # 5. Fetch 1-minute intraday data
        ticker = yf.Ticker(symbol)
        # Get enough data to cover the delay and current time
        data = ticker.history(interval="1m", period="2d") #get last 2 days of 1min interval

        if data.empty:
            print(f"No 1-minute data available for {symbol}")
            return None, None
        
        # 6. Convert the index to Eastern Time.  CRUCIAL step.
        data.index = data.index.tz_convert('US/Eastern')


        # 7. Find the closest available timestamp to the target time.
        # Find the closest timestamp *before* the target time
        available_times = data.index[data.index <= target_time]
        if available_times.empty:
             print(f"No data available for {symbol} before {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
             return None, None
            
        closest_timestamp = available_times.max() # Get latest available

        # 8. Extract the price
        price = data['Close'][closest_timestamp]
        timestamp_str = closest_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')

        return float(price), timestamp_str

    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, None

# --- Main execution ---
if __name__ == "__main__":
    tiingo_api_key = os.environ.get("TIINGO_API_KEY")
    if not tiingo_api_key:
        print("Error: TIINGO_API_KEY environment variable not set.")
        exit(1)

    symbol = "GOOG"  # Replace with your desired stock symbol
    delay_minutes = 15

    price, source, timestamp = get_intraday_price_tiingo_or_yfinance(symbol, tiingo_api_key, delay_minutes)

    if price is not None:
        print(f"Approximate {delay_minutes}-minute delayed price for {symbol} (at {timestamp}, source: {source}): ${price:.2f}")
    else:
        print(f"Could not retrieve an approximate delayed price for {symbol}.")