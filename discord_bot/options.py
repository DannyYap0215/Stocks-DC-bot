import yfinance as yf
from stock_data import POPULAR_TICKERS

def scan_unusual_options(limit=5):
    """
    Scans a few popular tickers for highly unusual options flow.
    We look for volume that is significantly higher than open interest.
    """
    # Keep it to a small subset so the bot command doesn't time out
    tickers_to_scan = ["NVDA", "AAPL", "TSLA", "AMD", "SPY", "QQQ"]
    whale_alerts = []

    for ticker_symbol in tickers_to_scan:
        try:
            ticker = yf.Ticker(ticker_symbol)
            dates = ticker.options

            if not dates:
                continue

            # Check the nearest expiration date
            opt = ticker.option_chain(dates[0])

            # Helper to process calls and puts
            def process_chain(chain, opt_type):
                # Filter for contracts with some baseline volume to avoid noise
                active = chain[(chain['volume'] > 500) & (chain['openInterest'] > 0)].copy()
                if active.empty:
                    return

                # Calculate volume / open interest ratio
                active['vol_oi_ratio'] = active['volume'] / active['openInterest']

                # Find massive outliers (e.g. Volume is 5x Open Interest)
                unusual = active[active['vol_oi_ratio'] > 5.0]

                for _, row in unusual.iterrows():
                    whale_alerts.append({
                        'ticker': ticker_symbol,
                        'type': opt_type,
                        'strike': row['strike'],
                        'exp': dates[0],
                        'volume': int(row['volume']),
                        'oi': int(row['openInterest']),
                        'ratio': row['vol_oi_ratio']
                    })

            process_chain(opt.calls, "CALL")
            process_chain(opt.puts, "PUT")

        except Exception as e:
            print(f"Error scanning options for {ticker_symbol}: {e}")

    # Sort by the most unusual ratio
    whale_alerts.sort(key=lambda x: x['ratio'], reverse=True)

    if not whale_alerts:
        return "No massive whale flow detected in standard tech tickers right now."

    result = "🐋 **[UNUSUAL WHALE OPTIONS FLOW]** 🐋\n\n"
    for alert in whale_alerts[:limit]:
        emoji = "📈" if alert['type'] == 'CALL' else "📉"
        result += f"{emoji} **{alert['ticker']}** ${alert['strike']} {alert['type']} (Exp: {alert['exp']})\n"
        result += f"└ Vol: **{alert['volume']}** | OI: {alert['oi']} (*{alert['ratio']:.1f}x ratio*)\n\n"

    return result
