import yfinance as yf
from langchain_core.tools import tool


@tool
def get_stock_price(ticker: str) -> str:
    """
    Get the current stock price, today's change, volume, and 52-week range
    for any stock ticker symbol (e.g. AAPL, TSLA, INFY.NS, RELIANCE.NS).
    Uses yfinance — free, no API key required.
    """
    symbol = ticker.upper().strip()
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="2d")
        info = stock.info

        if hist.empty:
            return f"No data found for ticker '{symbol}'. Check the symbol."

        current = hist["Close"].iloc[-1]
        prev_close = hist["Close"].iloc[-2] if len(hist) >= 2 else hist["Open"].iloc[-1]
        change = current - prev_close
        pct = (change / prev_close) * 100
        volume = hist["Volume"].iloc[-1]

        return (
            f"Stock : {info.get('longName', symbol)} ({symbol})\n"
            f"Price : ${current:.2f}\n"
            f"Change: {change:+.2f} ({pct:+.2f}%) vs previous close\n"
            f"Volume: {volume:,.0f}\n"
            f"52w High : ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52w Low  : ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
            f"Market Cap: ${info.get('marketCap', 0):,.0f}\n"
            f"Sector: {info.get('sector', 'N/A')}"
        )
    except Exception as e:
        return f"Could not fetch data for '{symbol}': {str(e)}"
