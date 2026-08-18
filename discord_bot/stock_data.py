import yfinance as yf
import pandas as pd
import datetime

# A simplified list of popular/major stocks to avoid rate limits
POPULAR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA",
    "JPM", "V", "WMT", "JNJ", "PG", "MA", "HD", "CVX",
    "MRK", "KO", "PEP", "COST", "BAC", "DIS", "NFLX",
    "AMD", "INTC", "CSCO"
]

def calculate_rsi(data, periods=14):
    """Calculates the Relative Strength Index (RSI)."""
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)

    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()

    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

def get_stock_metrics(ticker_symbol):
    """Fetches key metrics for a given ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        # We need historical data for RSI and growth metrics
        hist = ticker.history(period="6mo")
        if hist.empty:
            return None

        hist['RSI'] = calculate_rsi(hist)
        current_rsi = hist['RSI'].iloc[-1]

        # Calculate recent growth (e.g., 3 month change)
        if len(hist) > 60:
            price_3m_ago = hist['Close'].iloc[-60]
            current_price = hist['Close'].iloc[-1]
            growth_3m = ((current_price - price_3m_ago) / price_3m_ago) * 100
        else:
            growth_3m = 0

        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)

        # Use forward PE if trailing PE is not available
        pe_to_use = pe_ratio if pe_ratio else forward_pe

        return {
            'ticker': ticker_symbol,
            'pe_ratio': pe_to_use,
            'rsi': current_rsi,
            'growth_3m': growth_3m,
            'name': info.get('shortName', ticker_symbol)
        }
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def analyze_stocks():
    """Scans popular stocks and categorizes them."""
    undervalued = []
    growth = []
    fomo = []

    for ticker in POPULAR_TICKERS:
        metrics = get_stock_metrics(ticker)
        if not metrics:
            continue

        pe = metrics['pe_ratio']
        rsi = metrics['rsi']
        growth_3m = metrics['growth_3m']

        # Criteria for Undervalued: P/E ratio is relatively low (e.g., < 15) and RSI is not overbought (< 70)
        if pe and pe > 0 and pe < 15 and (pd.isna(rsi) or rsi < 70):
            undervalued.append(metrics)

        # Criteria for Growth: Steady 3-month growth (e.g., 5% to 25%), not overhyped (RSI < 70)
        if 5 <= growth_3m <= 25 and (pd.isna(rsi) or rsi < 70):
            growth.append(metrics)

        # Criteria for FOMO (Avoid): Very high RSI (> 70) indicating overbought, or massive recent spike (> 30% in 3 months)
        if (not pd.isna(rsi) and rsi > 70) or growth_3m > 30:
            fomo.append(metrics)

    # Sort them for better presentation
    undervalued = sorted(undervalued, key=lambda x: x['pe_ratio'] if x['pe_ratio'] else 999)[:5]
    growth = sorted(growth, key=lambda x: x['growth_3m'], reverse=True)[:5]
    fomo = sorted(fomo, key=lambda x: x['rsi'] if not pd.isna(x['rsi']) else 0, reverse=True)[:5]

    return {
        'undervalued': undervalued,
        'growth': growth,
        'fomo': fomo
    }

def format_stock_list(stock_list, category):
    """Formats a list of stocks into a readable string."""
    if not stock_list:
        return f"No {category} stocks found at the moment."

    result = f"**Top {category} Stocks:**\n"
    for stock in stock_list:
        pe_str = f"{stock['pe_ratio']:.2f}" if stock['pe_ratio'] else "N/A"
        rsi_str = f"{stock['rsi']:.2f}" if not pd.isna(stock['rsi']) else "N/A"

        result += f"• **{stock['ticker']}** ({stock['name']})\n"
        result += f"  - P/E: {pe_str} | RSI: {rsi_str} | 3M Growth: {stock['growth_3m']:.2f}%\n"

    return result
