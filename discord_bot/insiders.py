import yfinance as yf
import pandas as pd

def get_insider_trades(ticker_symbol):
    """
    Fetches recent significant insider trades for a given ticker.
    Excludes $0 transactions (like stock grants or gifts).
    """
    ticker_symbol = ticker_symbol.upper()
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.insider_transactions

        if df is None or df.empty:
            return f"No insider trading data found for **{ticker_symbol}**."

        # Filter out $0 transactions (grants/gifts) to only show actual buying/selling
        if 'Value' in df.columns:
            # yfinance sometimes returns missing values or NaNs in 'Value'
            df = df.dropna(subset=['Value'])
            df = df[df['Value'] > 0]

        if df.empty:
            return f"No recent significant insider trades (>$0) found for **{ticker_symbol}**."

        # Sort by most recent
        if 'Start Date' in df.columns:
            df = df.sort_values(by='Start Date', ascending=False)

        # Take the top 5
        top_trades = df.head(5).to_dict('records')

        result = f"👔 **Recent Insider Trades for {ticker_symbol}** 👔\n\n"

        for trade in top_trades:
            insider = trade.get('Insider', 'Unknown Insider')
            position = trade.get('Position', 'Unknown Position')
            text = trade.get('Text', '')
            shares = trade.get('Shares', 0)
            value = trade.get('Value', 0)
            date = trade.get('Start Date')

            # Format the date nicely if it exists
            if pd.notna(date):
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = "Unknown Date"

            # Determine action based on the text description
            action = "📉 SOLD" if "Sale" in text else "📈 BOUGHT" if "Purchase" in text or "Buy" in text else "🔄 TRADED"

            result += f"**{insider}** (*{position}*)\n"
            result += f"• **Action:** {action} {int(shares):,} shares\n"
            result += f"• **Value:** ${int(value):,}\n"
            result += f"• **Date:** {date_str}\n\n"

        return result

    except Exception as e:
        print(f"Error fetching insider trades for {ticker_symbol}: {e}")
        return f"❌ Error fetching insider data for **{ticker_symbol}**. The API might be rate limited or the ticker is invalid."

if __name__ == "__main__":
    print(get_insider_trades("AAPL"))
