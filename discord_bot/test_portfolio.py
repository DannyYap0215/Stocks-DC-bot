import unittest
from unittest.mock import patch, mock_open
import portfolio

class TestPortfolio(unittest.TestCase):
    @patch('portfolio.json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_portfolios(self, mock_file, mock_json_dump):
        test_data = {'user123': {'AAPL': {'shares': 10, 'total_cost': 1500.0}}}

        portfolio.save_portfolios(test_data)

        mock_file.assert_called_once_with(portfolio.PORTFOLIO_FILE, 'w')
        mock_json_dump.assert_called_once_with(test_data, mock_file.return_value, indent=4)

if __name__ == '__main__':
    unittest.main()
