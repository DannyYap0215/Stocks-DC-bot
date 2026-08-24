import pandas as pd
import pytest
from discord_bot.stock_data import calculate_rsi

def test_calculate_rsi_empty_dataframe():
    # Arrange
    data = pd.DataFrame(columns=['Close'])

    # Act
    result = calculate_rsi(data)

    # Assert
    assert isinstance(result, pd.Series)
    assert result.empty

def test_calculate_rsi_single_row():
    # Arrange
    data = pd.DataFrame({'Close': [100.0]})

    # Act
    result = calculate_rsi(data)

    # Assert
    assert isinstance(result, pd.Series)
    assert pd.isna(result.iloc[0]) # With one value diff() is NaN, ewma is NaN

def test_calculate_rsi_less_than_periods():
    # Arrange
    # Default periods is 14. Let's pass 5 rows.
    data = pd.DataFrame({'Close': [100, 102, 104, 103, 105]})

    # Act
    result = calculate_rsi(data, periods=14)

    # Assert
    assert isinstance(result, pd.Series)
    assert len(result) == 5
    # The minimum periods required to calculate valid ewma output is periods (14).
    # Therefore, all 5 rows should have NaN for RSI.
    assert result.isna().all()

def test_calculate_rsi_standard():
    # Arrange
    # Provide enough data to calculate valid RSI (at least periods)
    # Using 15 rows for periods=14
    data = pd.DataFrame({'Close': [
        44.34, 44.09, 44.15, 43.61, 44.33,
        44.83, 45.10, 45.42, 45.84, 46.08,
        45.89, 46.03, 45.61, 46.28, 46.28
    ]})

    # Act
    result = calculate_rsi(data, periods=14)

    # Assert
    assert isinstance(result, pd.Series)
    assert len(result) == 15
    # The first 13 elements should be NaN due to min_periods=14 in ewm
    assert result.iloc[:13].isna().all()
    # With min_periods=14 on a diff() array (which loses the first row),
    # we need 15 rows to get 14 valid diffs to compute the ewma.
    # Therefore, the first 14 elements (indices 0 to 13) will be NaN,
    # and the 15th element (index 14) will have the first valid RSI.
    assert result.iloc[:14].isna().all()
    assert not pd.isna(result.iloc[14])

    # Basic bounds check for RSI
    assert 0 <= result.iloc[14] <= 100
