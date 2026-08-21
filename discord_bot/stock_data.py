import yfinance as yf
import pandas as pd
import datetime
import urllib.request
import json
import time

# A focused list of tech, memory, and semiconductor stocks, plus VXUS
POPULAR_TICKERS = [
    "NVDA", "MU", "WDC", "TSM", "AMD", "ASML", "INTC",
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO",
    "QCOM", "TXN", "AMAT", "LRCX", "KLAC", "SNPS", "CDNS",
    "ARM", "SMCI", "STX", "VXUS"
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

# Simple TTL caches to avoid hitting rate limits
_metrics_cache = {}
_live_price_cache = {}
CACHE_TTL = 300 # 5 minutes

def get_stock_metrics(ticker_symbol):
    """Fetches key metrics for a given ticker, with a 5-minute TTL cache."""
    ticker_symbol = ticker_symbol.upper()
    current_time = time.time()

    # Check cache first
    if ticker_symbol in _metrics_cache:
        cached_data, timestamp = _metrics_cache[ticker_symbol]
        if current_time - timestamp < CACHE_TTL:
            return cached_data

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

        result = {
            'ticker': ticker_symbol,
            'pe_ratio': pe_to_use,
            'rsi': current_rsi,
            'growth_3m': growth_3m,
            'name': info.get('shortName', ticker_symbol)
        }

        # Save to cache
        _metrics_cache[ticker_symbol] = (result, current_time)
        return result
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")

        # If rate limited but we have stale cache, return it rather than failing
        if ticker_symbol in _metrics_cache:
            return _metrics_cache[ticker_symbol][0]

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


def get_live_price(ticker_symbol):
    """Fetches the real-time live price of a given ticker, with a 60-second TTL cache."""
    ticker_symbol = ticker_symbol.upper()
    current_time = time.time()

    # Check cache first (shorter 60s TTL for live prices)
    if ticker_symbol in _live_price_cache:
        cached_data, timestamp = _live_price_cache[ticker_symbol]
        if current_time - timestamp < 60:
            return cached_data

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

            # Robust null-checking before accessing dictionary keys
            chart = data.get('chart', {})
            result = chart.get('result')

            if not result or not isinstance(result, list) or len(result) == 0:
                raise Exception("API response missing 'result' array")

            meta = result[0].get('meta')
            if not meta:
                raise Exception("API response missing 'meta' object")

            price = meta.get('regularMarketPrice')
            prev_close = meta.get('chartPreviousClose')

            if price is None:
                raise Exception("Missing regularMarketPrice in meta")

            change = None
            change_pct = None

            if prev_close and prev_close > 0:
                change = price - prev_close
                change_pct = (change / prev_close) * 100

            result = {
                'ticker': ticker_symbol,
                'price': price,
                'change': change,
                'change_pct': change_pct
            }
            _live_price_cache[ticker_symbol] = (result, current_time)
            return result
    except Exception as e:
        print(f"Error fetching live price for {ticker_symbol} via Yahoo API: {e}")

        # Fallback to yfinance if direct API fails
        try:
            ticker = yf.Ticker(ticker_symbol)
            price = ticker.fast_info.get("lastPrice")
            prev_close = ticker.fast_info.get("previousClose")

            if price is None:
                return None

            change = None
            change_pct = None

            if prev_close and prev_close > 0:
                change = price - prev_close
                change_pct = (change / prev_close) * 100

            result = {
                'ticker': ticker_symbol,
                'price': price,
                'change': change,
                'change_pct': change_pct
            }
            _live_price_cache[ticker_symbol] = (result, current_time)
            return result
        except Exception as fallback_e:
            print(f"Fallback yfinance error for {ticker_symbol}: {fallback_e}")

            # If rate limited but we have stale cache, return it
            if ticker_symbol in _live_price_cache:
                return _live_price_cache[ticker_symbol][0]

            return None

def scan_unusual_activity():
    """Scans popular stocks for major price swings."""
    alerts = []

    for ticker in POPULAR_TICKERS:
        data = get_live_price(ticker)
        if not data or data['change_pct'] is None:
            continue

        change_pct = data['change_pct']
        price = data['price']

        # Flag if the stock moved more than 5% up or down today
        if abs(change_pct) >= 5.0:
            direction = "🚀 SURGING" if change_pct > 0 else "🩸 PLUNGING"
            emoji = "🟢" if change_pct > 0 else "🔴"

            alerts.append({
                'ticker': ticker,
                'price': price,
                'change_pct': change_pct,
                'direction': direction,
                'emoji': emoji
            })

    # Sort alerts by biggest absolute move
    alerts.sort(key=lambda x: abs(x['change_pct']), reverse=True)
    return alerts

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
