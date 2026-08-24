import unittest
import pandas as pd
from stock_data import format_stock_list

class TestFormatStockList(unittest.TestCase):
    def test_empty_stock_list(self):
        result = format_stock_list([], "Tech")
        self.assertEqual(result, "No Tech stocks found at the moment.")

    def test_valid_stock_list(self):
        stock_list = [
            {
                'ticker': 'AAPL',
                'name': 'Apple Inc.',
                'pe_ratio': 28.5,
                'rsi': 55.2,
                'growth_3m': 12.4
            },
            {
                'ticker': 'MSFT',
                'name': 'Microsoft',
                'pe_ratio': 35.1,
                'rsi': 60.1,
                'growth_3m': 8.9
            }
        ]
        result = format_stock_list(stock_list, "Tech")

        expected_result = "**Top Tech Stocks:**\n"
        expected_result += "• **AAPL** (Apple Inc.)\n"
        expected_result += "  - P/E: 28.50 | RSI: 55.20 | 3M Growth: 12.40%\n"
        expected_result += "• **MSFT** (Microsoft)\n"
        expected_result += "  - P/E: 35.10 | RSI: 60.10 | 3M Growth: 8.90%\n"

        self.assertEqual(result, expected_result)

    def test_missing_pe_and_na_rsi(self):
        stock_list = [
            {
                'ticker': 'TSLA',
                'name': 'Tesla',
                'pe_ratio': None,  # Missing P/E
                'rsi': pd.NA,      # Missing RSI
                'growth_3m': -5.2
            },
            {
                'ticker': 'AMZN',
                'name': 'Amazon',
                'pe_ratio': 0,     # Falsy P/E
                'rsi': float('nan'), # Missing RSI as float nan
                'growth_3m': 15.0
            }
        ]
        result = format_stock_list(stock_list, "Growth")

        expected_result = "**Top Growth Stocks:**\n"
        expected_result += "• **TSLA** (Tesla)\n"
        expected_result += "  - P/E: N/A | RSI: N/A | 3M Growth: -5.20%\n"
        expected_result += "• **AMZN** (Amazon)\n"
        expected_result += "  - P/E: N/A | RSI: N/A | 3M Growth: 15.00%\n"

        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
