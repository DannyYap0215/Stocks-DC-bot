import unittest
from unittest.mock import patch, mock_open
import sys
import os

# Add the parent directory to sys.path so we can import from discord_bot
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from portfolio import load_portfolios, PORTFOLIO_FILE
import json

class TestPortfolioLoad(unittest.TestCase):

    @patch('os.path.exists')
    def test_load_portfolios_file_not_exists(self, mock_exists):
        """Test load_portfolios when the portfolio file does not exist."""
        mock_exists.return_value = False
        result = load_portfolios()
        self.assertEqual(result, {})
        mock_exists.assert_called_once_with(PORTFOLIO_FILE)

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{"user1": {"AAPL": {"shares": 10.0, "total_cost": 1500.0}}}')
    def test_load_portfolios_file_exists_valid_json(self, mock_file, mock_exists):
        """Test load_portfolios when the portfolio file exists and contains valid JSON."""
        mock_exists.return_value = True
        result = load_portfolios()
        expected = {"user1": {"AAPL": {"shares": 10.0, "total_cost": 1500.0}}}
        self.assertEqual(result, expected)
        mock_exists.assert_called_once_with(PORTFOLIO_FILE)
        mock_file.assert_called_once_with(PORTFOLIO_FILE, 'r')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='{invalid json')
    def test_load_portfolios_file_exists_invalid_json(self, mock_file, mock_exists):
        """Test load_portfolios when the portfolio file exists but contains invalid JSON."""
        mock_exists.return_value = True
        result = load_portfolios()
        self.assertEqual(result, {})
        mock_exists.assert_called_once_with(PORTFOLIO_FILE)
        mock_file.assert_called_once_with(PORTFOLIO_FILE, 'r')

if __name__ == '__main__':
    unittest.main()
