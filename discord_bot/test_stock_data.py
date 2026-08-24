import unittest
from unittest.mock import patch
import stock_data

class TestAnalyzeStocks(unittest.TestCase):

    @patch('stock_data.POPULAR_TICKERS', ['TEST'])
    @patch('stock_data.get_stock_metrics')
    def test_undervalued_stock(self, mock_get_metrics):
        # Criteria for Undervalued: P/E ratio is relatively low (e.g., < 15) and RSI is not overbought (< 70)
        mock_metrics = {
            'ticker': 'TEST',
            'pe_ratio': 10,
            'rsi': 50,
            'growth_3m': 2,
            'name': 'Test Company'
        }
        mock_get_metrics.return_value = mock_metrics

        results = stock_data.analyze_stocks()

        self.assertEqual(len(results['undervalued']), 1)
        self.assertEqual(results['undervalued'][0]['ticker'], 'TEST')
        self.assertEqual(len(results['growth']), 0)
        self.assertEqual(len(results['fomo']), 0)

    @patch('stock_data.POPULAR_TICKERS', ['GROW'])
    @patch('stock_data.get_stock_metrics')
    def test_growth_stock(self, mock_get_metrics):
        # Criteria for Growth: Steady 3-month growth (e.g., 5% to 25%), not overhyped (RSI < 70)
        mock_metrics = {
            'ticker': 'GROW',
            'pe_ratio': 20,
            'rsi': 60,
            'growth_3m': 15,
            'name': 'Growth Company'
        }
        mock_get_metrics.return_value = mock_metrics

        results = stock_data.analyze_stocks()

        self.assertEqual(len(results['growth']), 1)
        self.assertEqual(results['growth'][0]['ticker'], 'GROW')
        self.assertEqual(len(results['undervalued']), 0)
        self.assertEqual(len(results['fomo']), 0)

    @patch('stock_data.POPULAR_TICKERS', ['FOMO1', 'FOMO2'])
    @patch('stock_data.get_stock_metrics')
    def test_fomo_stock(self, mock_get_metrics):
        # Criteria for FOMO (Avoid): Very high RSI (> 70) indicating overbought, or massive recent spike (> 30% in 3 months)
        def side_effect(ticker):
            if ticker == 'FOMO1':
                return {
                    'ticker': 'FOMO1',
                    'pe_ratio': 50,
                    'rsi': 80, # High RSI
                    'growth_3m': 10,
                    'name': 'High RSI Company'
                }
            elif ticker == 'FOMO2':
                return {
                    'ticker': 'FOMO2',
                    'pe_ratio': 50,
                    'rsi': 50,
                    'growth_3m': 40, # Massive spike
                    'name': 'High Growth Company'
                }
        mock_get_metrics.side_effect = side_effect

        results = stock_data.analyze_stocks()

        self.assertEqual(len(results['fomo']), 2)
        fomo_tickers = [s['ticker'] for s in results['fomo']]
        self.assertIn('FOMO1', fomo_tickers)
        self.assertIn('FOMO2', fomo_tickers)
        self.assertEqual(len(results['undervalued']), 0)
        self.assertEqual(len(results['growth']), 0)

    @patch('stock_data.POPULAR_TICKERS', ['MISSING'])
    @patch('stock_data.get_stock_metrics')
    def test_missing_metrics(self, mock_get_metrics):
        mock_get_metrics.return_value = None

        results = stock_data.analyze_stocks()

        self.assertEqual(len(results['undervalued']), 0)
        self.assertEqual(len(results['growth']), 0)
        self.assertEqual(len(results['fomo']), 0)

    @patch('stock_data.POPULAR_TICKERS', [f'U{i}' for i in range(1, 8)] + [f'G{i}' for i in range(1, 8)] + [f'F{i}' for i in range(1, 8)])
    @patch('stock_data.get_stock_metrics')
    def test_sorting_and_truncation(self, mock_get_metrics):
        def side_effect(ticker):
            # Undervalued: P/E < 15, RSI < 70
            if ticker.startswith('U'):
                val = int(ticker[1:])
                return {
                    'ticker': ticker,
                    'pe_ratio': val,  # U1 (1) -> U7 (7)
                    'rsi': 50,
                    'growth_3m': 2,
                    'name': ticker
                }
            # Growth: 5 <= growth_3m <= 25, RSI < 70
            elif ticker.startswith('G'):
                val = int(ticker[1:])
                return {
                    'ticker': ticker,
                    'pe_ratio': 20,
                    'rsi': 50,
                    'growth_3m': 5 + val, # G1 (6) -> G7 (12)
                    'name': ticker
                }
            # FOMO: RSI > 70
            elif ticker.startswith('F'):
                val = int(ticker[1:])
                return {
                    'ticker': ticker,
                    'pe_ratio': 20,
                    'rsi': 70 + val, # F1 (71) -> F7 (77)
                    'growth_3m': 2,
                    'name': ticker
                }
        mock_get_metrics.side_effect = side_effect

        results = stock_data.analyze_stocks()

        # Verify length is capped at 5
        self.assertEqual(len(results['undervalued']), 5)
        self.assertEqual(len(results['growth']), 5)
        self.assertEqual(len(results['fomo']), 5)

        # Verify sorting
        # Undervalued sorted by lowest pe_ratio
        u_tickers = [s['ticker'] for s in results['undervalued']]
        self.assertEqual(u_tickers, ['U1', 'U2', 'U3', 'U4', 'U5'])

        # Growth sorted by highest growth_3m
        g_tickers = [s['ticker'] for s in results['growth']]
        self.assertEqual(g_tickers, ['G7', 'G6', 'G5', 'G4', 'G3'])

        # FOMO sorted by highest rsi
        f_tickers = [s['ticker'] for s in results['fomo']]
        self.assertEqual(f_tickers, ['F7', 'F6', 'F5', 'F4', 'F3'])

if __name__ == '__main__':
    unittest.main()
