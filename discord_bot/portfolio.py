import json
import os
import yfinance as yf

PORTFOLIO_FILE = 'portfolios.json'

def load_portfolios():
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_portfolios(data):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def add_to_portfolio(user_id, ticker, shares, price_paid):
    data = load_portfolios()
    user_id_str = str(user_id)

    if user_id_str not in data:
        data[user_id_str] = {}

    ticker = ticker.upper()
    if ticker not in data[user_id_str]:
        data[user_id_str][ticker] = {'shares': 0.0, 'total_cost': 0.0}

    # Update position (average down/up)
    current_shares = data[user_id_str][ticker]['shares']
    current_cost = data[user_id_str][ticker]['total_cost']

    new_cost = price_paid * shares
    data[user_id_str][ticker]['shares'] = current_shares + shares
    data[user_id_str][ticker]['total_cost'] = current_cost + new_cost

    save_portfolios(data)
    return True

def view_portfolio(user_id):
    data = load_portfolios()
    user_id_str = str(user_id)

    if user_id_str not in data or not data[user_id_str]:
        return "Your portfolio is empty. Add stocks using `!portfolio add <ticker> <shares> <price>`."

    portfolio = data[user_id_str]
    result = "💼 **Your Portfolio:**\n\n"

    total_value = 0
    total_cost_basis = 0

    for ticker, info in portfolio.items():
        shares = info['shares']
        avg_price = info['total_cost'] / shares if shares > 0 else 0
        total_cost_basis += info['total_cost']

        try:
            # Get current price
            from stock_data import get_live_price
            price_data = get_live_price(ticker)

            if not price_data or price_data['price'] is None:
                raise ValueError("No price data found.")

            current_price = price_data['price']
            value = current_price * shares
            total_value += value

            profit_loss = value - info['total_cost']
            pl_percent = (profit_loss / info['total_cost']) * 100 if info['total_cost'] > 0 else 0

            emoji = "🟢" if profit_loss >= 0 else "🔴"

            result += f"**{ticker}** ({shares:g} shares @ ${avg_price:.2f} avg)\n"
            result += f"└ Current: ${current_price:.2f} | Value: ${value:.2f} | P/L: {emoji} ${profit_loss:.2f} ({pl_percent:.2f}%)\n\n"

        except Exception as e:
            result += f"**{ticker}** ({shares:g} shares @ ${avg_price:.2f} avg)\n"
            result += f"└ ⚠️ *Error fetching current price*\n\n"

    total_pl = total_value - total_cost_basis
    total_pl_percent = (total_pl / total_cost_basis) * 100 if total_cost_basis > 0 else 0
    total_emoji = "🟢" if total_pl >= 0 else "🔴"

    result += f"**Total Portfolio Value:** ${total_value:.2f}\n"
    result += f"**Total Return:** {total_emoji} ${total_pl:.2f} ({total_pl_percent:.2f}%)\n"

    return result
