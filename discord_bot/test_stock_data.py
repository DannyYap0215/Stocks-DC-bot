import unittest
import pandas as pd
import numpy as np

from stock_data import calculate_rsi

class TestStockData(unittest.TestCase):
    def test_calculate_rsi_normal(self):
        # Create a sample dataframe with 20 days of data to satisfy default periods=14
        data = {
            'Close': [
                44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
                45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00,
                46.03, 46.41, 46.22, 45.64
            ]
        }
        df = pd.DataFrame(data)
        rsi = calculate_rsi(df, periods=14)

        self.assertEqual(len(rsi), 20)
        # First element is usually NaN because it diff() is NaN
        self.assertTrue(pd.isna(rsi.iloc[0]))

        # Test values are between 0 and 100 for the valid period
        for val in rsi.dropna():
            self.assertGreaterEqual(val, 0)
            self.assertLessEqual(val, 100)

        # The last value should be close to calculated RSI for this known sequence
        # We just verify it's a valid float
        self.assertFalse(pd.isna(rsi.iloc[-1]))

    def test_calculate_rsi_insufficient_data(self):
        # DataFrame smaller than the number of periods
        data = {'Close': [10, 11, 12, 13, 14]}
        df = pd.DataFrame(data)

        rsi = calculate_rsi(df, periods=14)

        # In pandas EWM, with min_periods=14, all outputs should be NaN
        # Wait, min_periods is for the ewm calculation
        self.assertTrue(rsi.isna().all())

    def test_calculate_rsi_upward_trend(self):
        # Strict upward trend should lead to high RSI approaching 100
        data = {'Close': [10 + i for i in range(20)]}
        df = pd.DataFrame(data)

        rsi = calculate_rsi(df, periods=14)

        # Last value should be 100 since there's no downward movement
        self.assertAlmostEqual(rsi.iloc[-1], 100.0, places=2)

    def test_calculate_rsi_downward_trend(self):
        # Strict downward trend should lead to low RSI approaching 0
        data = {'Close': [100 - i for i in range(20)]}
        df = pd.DataFrame(data)

        rsi = calculate_rsi(df, periods=14)

        # Last value should be 0 since there's no upward movement
        self.assertAlmostEqual(rsi.iloc[-1], 0.0, places=2)

    def test_calculate_rsi_flat_trend(self):
        # Constant prices
        data = {'Close': [50] * 20}
        df = pd.DataFrame(data)

        rsi = calculate_rsi(df, periods=14)

        # In calculate_rsi, ma_up and ma_down will both be 0.
        # rsi = ma_up / ma_down -> 0/0 which is NaN.
        # So rsi should be NaN.
        self.assertTrue(rsi.isna().all())

if __name__ == '__main__':
    unittest.main()