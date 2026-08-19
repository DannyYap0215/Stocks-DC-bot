import yfinance as yf
import mplfinance as mpf
import io
import discord

def generate_chart(ticker_symbol, period="3mo"):
    """
    Generates a candlestick chart for a given ticker and returns it as a Discord File object.
    Returns None if the ticker is invalid or data is unavailable.
    """
    try:
        ticker = yf.Ticker(ticker_symbol.upper())
        hist = ticker.history(period=period)

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
        print(f"Error generating chart for {ticker_symbol}: {e}")
        return None
