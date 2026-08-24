import mplfinance as mpf
import io
import discord
import urllib.request
import json
import pandas as pd

def generate_chart(ticker_symbol, period="6mo"):
    """
    Generates an advanced candlestick chart with Bollinger Bands and MACD.
    Returns None if the ticker is invalid or data is unavailable.
    """
    ticker_symbol = ticker_symbol.upper()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}?range={period}&interval=1d"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

            result_list = data.get('chart', {}).get('result')
            if not result_list or not isinstance(result_list, list) or len(result_list) == 0:
                return None

            result = result_list[0]

            if 'timestamp' not in result or 'indicators' not in result:
                return None

            timestamps = result['timestamp']
            quote = result['indicators']['quote'][0]

            hist = pd.DataFrame({
                'Open': quote.get('open', []),
                'High': quote.get('high', []),
                'Low': quote.get('low', []),
                'Close': quote.get('close', []),
                'Volume': quote.get('volume', [])
            })

            # Convert timestamp to datetime and set as index
            hist.index = pd.to_datetime(timestamps, unit='s')

            if hist.empty:
                return None

            # --- Technical Indicators Calculation ---

            # Bollinger Bands (20-day SMA, 2 standard deviations)
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['STD_20'] = hist['Close'].rolling(window=20).std()
            hist['Upper_Band'] = hist['SMA_20'] + (hist['STD_20'] * 2)
            hist['Lower_Band'] = hist['SMA_20'] - (hist['STD_20'] * 2)

            # MACD (12-day EMA - 26-day EMA)
            exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = exp1 - exp2
            hist['Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            hist['MACD_Hist'] = hist['MACD'] - hist['Signal']

        # --- Plotting ---
        buf = io.BytesIO()

        # Define additional plots for Bollinger Bands (Panel 0) and MACD (Panel 2)
        # Volume automatically goes to Panel 1 if we set volume_panel=1
        apdict = [
            # Bollinger Bands
            mpf.make_addplot(hist['Upper_Band'], color='g', alpha=0.3, panel=0),
            mpf.make_addplot(hist['Lower_Band'], color='r', alpha=0.3, panel=0),

            # MACD
            mpf.make_addplot(hist['MACD'], panel=2, color='fuchsia', ylabel='MACD'),
            mpf.make_addplot(hist['Signal'], panel=2, color='b'),
            mpf.make_addplot(hist['MACD_Hist'], type='bar', width=0.7, panel=2, color='dimgray', alpha=1, secondary_y=False),
        ]

        kwargs = dict(
            type='candle',
            volume=True,
            volume_panel=1,
            title=f'\n{ticker_symbol.upper()} - {period}',
            ylabel='Price ($)',
            ylabel_lower='Volume',
            style='yahoo',
            figsize=(12, 8),
            panel_ratios=(6, 2, 2)
        )

        mpf.plot(hist, **kwargs, addplot=apdict, savefig=dict(fname=buf, dpi=100, bbox_inches='tight'))
        buf.seek(0)

        return discord.File(fp=buf, filename=f"chart_{ticker_symbol.upper()}.png")

    except Exception as e:
        error_str = str(e).lower()
        if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str or "expecting value" in error_str:
            print(f"Rate limit error generating chart for {ticker_symbol}: {e}")
            return "RATE_LIMITED"

        print(f"Error generating chart for {ticker_symbol}: {e}")
        return None
