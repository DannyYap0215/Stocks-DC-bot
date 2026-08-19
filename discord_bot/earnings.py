import yfinance as yf
import datetime
from stock_data import POPULAR_TICKERS

def get_upcoming_earnings():
    """
    Scans tracked tickers and returns a list of those reporting earnings in the next 14 days.
    """
    today = datetime.date.today()
    two_weeks = today + datetime.timedelta(days=14)

    upcoming = []

    for ticker_symbol in POPULAR_TICKERS:
        try:
            ticker = yf.Ticker(ticker_symbol)
            cal = ticker.calendar

            if not cal or 'Earnings Date' not in cal:
                continue

            earnings_dates = cal['Earnings Date']
            if not earnings_dates:
                continue

            next_date = earnings_dates[0]

            if today <= next_date <= two_weeks:
                upcoming.append({
                    'ticker': ticker_symbol,
                    'date': next_date
                })
        except Exception as e:
            pass # Ignore API errors for individual tickers

    upcoming.sort(key=lambda x: x['date'])

    if not upcoming:
        return "No major tracked companies reporting earnings in the next 14 days."

    result = "📅 **[UPCOMING EARNINGS (Next 14 Days)]** 📅\n\n"
    for item in upcoming:
        days_away = (item['date'] - today).days
        time_str = "Today!" if days_away == 0 else f"in {days_away} days"

        result += f"**{item['ticker']}**: {item['date'].strftime('%b %d, %Y')} ({time_str})\n"

    return result
