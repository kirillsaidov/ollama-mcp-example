# module mcp_server

# system
import json
from datetime import datetime, timedelta

# libs
import yfinance as yf
from fastmcp import FastMCP

# init mcp server instance
mcp = FastMCP("MongoDB MCP Server")


@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """Get the current stock price for a given symbol."""
    try:
        ticker = yf.Ticker(symbol)
        result = ticker.info.get('regularMarketPrice') or ticker.fast_info.last_price
    except Exception as e:
        result = str(e) # just return the error itself
    
    return result


@mcp.tool()
def get_stock_historical_data(symbol: str, period: str ='1mo', interval: str ='1d', start_date: str = None, end_date: str = None) -> dict:
    """Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT').
        period (str, optional): Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 
            5y, 10y, ytd, max. Used when start_date and end_date are not 
            specified. Defaults to '1mo'.
        interval (str, optional): Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 
            90m, 1h, 1d, 5d, 1wk, 1mo, 3mo. Defaults to '1d'.
        start_date (str, optional): Start date in 'YYYY-MM-DD' format. 
            If specified, period parameter is ignored. Defaults to None.
        end_date (str, optional): End date in 'YYYY-MM-DD' format. 
            If not specified, defaults to current date. Defaults to None.
    
    Returns:
        dict: Dictionary with the following structure:
            {
                "symbol": str,
                "interval": str,
                "period": str,
                "data_points": int,
                "date_range": {
                    "start": str,
                    "end": str
                },
                "data": [
                    {
                        "Date": str,
                        "Open": float,
                        "High": float,
                        "Low": float,
                        "Close": float,
                        "Volume": int,
                        "Adj Close": float
                    },
                    ...
                ]
            }
            Returns dict with 'error' field if no data is found or an error occurs.

    Note:
        Intraday data (1m, 2m, 5m, etc.) is limited to last 60 days.
        1m interval is limited to last 7 days.
    """
    # Create ticker object
    ticker = yf.Ticker(symbol)
    
    # Fetch data based on whether dates are specified
    if start_date and end_date:
        data = ticker.history(start=start_date, end=end_date, interval=interval)
    elif start_date:
        data = ticker.history(start=start_date, interval=interval)
    else:
        data = ticker.history(period=period, interval=interval)
    
    # Check if data is empty
    if data.empty:
        return {'error': f'No data found for symbol: {symbol}'}
    
    # Get descriptive statistics using pandas
    stats = data[['Open', 'High', 'Low', 'Close', 'Volume']].describe()
    
    # Calculate additional metrics
    price_change = float(data['Close'].iloc[-1] - data['Close'].iloc[0])
    percent_change = float((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0] * 100)
    
    # Build summary from pandas describe()
    summary = {
        "price_stats": {
            "open": {
                "mean": float(stats.loc['mean', 'Open']),
                "std": float(stats.loc['std', 'Open']),
                "min": float(stats.loc['min', 'Open']),
                "max": float(stats.loc['max', 'Open'])
            },
            "close": {
                "mean": float(stats.loc['mean', 'Close']),
                "std": float(stats.loc['std', 'Close']),
                "min": float(stats.loc['min', 'Close']),
                "max": float(stats.loc['max', 'Close'])
            }
        },
        "period_performance": {
            "starting_price": float(data['Close'].iloc[0]),
            "ending_price": float(data['Close'].iloc[-1]),
            "price_change": round(price_change, 2),
            "percent_change": round(percent_change, 2)
        },
    }
    
    # Reset index for sample data
    data_with_date = data.reset_index()
    data_with_date['Date'] = data_with_date['Date'].astype(str)
    
    # Round numeric values
    for col in ['Open', 'High', 'Low', 'Close']:
        data_with_date[col] = data_with_date[col].round(2)
    
    # Drop unnecessary columns
    data_with_date = data_with_date.drop(columns=['Dividends', 'Stock Splits'])
    
    # Build response dictionary
    result = {
        "symbol": symbol,
        "interval": interval,
        "period": period if not start_date else f"{start_date} to {end_date or 'now'}",
        "data_points": len(data),
        "date_range": {
            "start": str(data.index[0]),
            "end": str(data.index[-1])
        },
        "summary": summary,
        "sample_data": {
            "first_5_days": data_with_date.head(5).to_dict(orient='records'),
            "last_5_days": data_with_date.tail(5).to_dict(orient='records')
        }
    }

    return result


if __name__ == '__main__':
    mcp.run(transport='sse', port=8050)
