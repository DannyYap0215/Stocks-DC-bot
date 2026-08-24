import os
import json
import pytest
from unittest.mock import patch, mock_open
from portfolio import load_portfolios

def test_load_portfolios_file_not_exist():
    """Test that load_portfolios returns empty dict when file doesn't exist."""
    with patch('os.path.exists', return_value=False):
        assert load_portfolios() == {}

def test_load_portfolios_success():
    """Test that load_portfolios returns correct data when file exists and has valid JSON."""
    valid_json = '{"user1": {"AAPL": {"shares": 10, "total_cost": 1500.0}}}'
    expected_data = {"user1": {"AAPL": {"shares": 10, "total_cost": 1500.0}}}

    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=valid_json)):
            assert load_portfolios() == expected_data

def test_load_portfolios_json_decode_error():
    """Test that load_portfolios returns empty dict when file contains invalid JSON."""
    invalid_json = '{'  # Invalid JSON

    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=invalid_json)):
            assert load_portfolios() == {}
