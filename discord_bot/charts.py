import mplfinance as mpf
import io
import discord
import urllib.request
import json
import pandas as pd

def generate_chart(ticker_symbol, period="3mo"):
    """
    Generates a candlestick chart for a given ticker and returns it as a Discord File object.
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

        # Create an in-memory buffer to save the image
        buf = io.BytesIO()

        # Configure the plot
        kwargs = dict(
            type='candle',
            volume=True,
            title=f'\n{ticker_symbol.upper()} - {period}',
            ylabel='Price ($)',
            ylabel_lower='Volume',
            style='yahoo',
            mav=(20, 50), # 20 and 50 day moving averages
            figsize=(10, 6)
        )

        # Generate the plot and save it to the buffer
        mpf.plot(hist, **kwargs, savefig=dict(fname=buf, dpi=100, bbox_inches='tight'))
        buf.seek(0)

        return discord.File(fp=buf, filename=f"chart_{ticker_symbol.upper()}.png")

    except Exception as e:
        error_str = str(e).lower()
        if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str or "expecting value" in error_str:
            print(f"Rate limit error generating chart for {ticker_symbol}: {e}")
            return "RATE_LIMITED"

        print(f"Error generating chart for {ticker_symbol}: {e}")
        return None
