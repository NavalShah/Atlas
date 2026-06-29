import pytest
import pandas as pd
from atlas_quant.data.validator import validate_market_data

def test_validate_market_data_valid():
    """Test validation of valid data."""
    df = pd.DataFrame({
        "Open": [1.0, 2.0, 3.0],
        "High": [2.0, 3.0, 4.0],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.5, 2.5, 3.5],
        "Volume": [100, 200, 300]
    }, index=pd.date_range("2024-01-01", periods=3))
    errors = validate_market_data(df)
    assert errors == []

def test_validate_market_data_empty():
    """Test validation of empty DataFrame."""
    df = pd.DataFrame()
    errors = validate_market_data(df)
    assert "DataFrame is empty" in errors

def test_validate_market_data_missing_columns():
    """Test validation when columns are missing."""
    df = pd.DataFrame({
        "Open": [1.0, 2.0],
        "High": [2.0, 3.0]
        # Missing Low, Close, Volume
    }, index=pd.date_range("2024-01-01", periods=2))
    errors = validate_market_data(df)
    # Should complain about missing columns
    assert any("Missing columns" in e for e in errors)

def test_validate_market_data_negative_values():
    """Test validation of negative prices and volume."""
    df = pd.DataFrame({
        "Open": [1.0, -2.0, 3.0],  # Negative in second row
        "High": [2.0, 3.0, 4.0],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.5, 2.5, 3.5],
        "Volume": [100, 200, -300]  # Negative volume
    }, index=pd.date_range("2024-01-01", periods=3))
    errors = validate_market_data(df)
    # Should have errors about negative Open and Volume
    assert any("Open" in e and "negative" in e for e in errors)
    assert any("Volume" in e and "negative" in e for e in errors)

def test_validate_market_data_duplicate_index():
    """Test validation of duplicate index."""
    df = pd.DataFrame({
        "Open": [1.0, 2.0, 3.0],
        "High": [2.0, 3.0, 4.0],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.5, 2.5, 3.5],
        "Volume": [100, 200, 300]
    }, index=pd.date_range("2024-01-01", periods=3))
    # Duplicate the first date
    df.index = pd.DatetimeIndex(["2024-01-01", "2024-01-01", "2024-01-02"])
    errors = validate_market_data(df)
    assert any("Duplicate dates" in e for e in errors)

def test_validate_market_data_non_monotonic():
    """Test validation of non-monotonic index."""
    df = pd.DataFrame({
        "Open": [1.0, 2.0, 3.0],
        "High": [2.0, 3.0, 4.0],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.5, 2.5, 3.5],
        "Volume": [100, 200, 300]
    }, index=pd.date_range("2024-01-03", periods=3))  # Starting at 2024-01-03, then 2024-01-04, then 2024-01-05
    # Shuffle to make non-monotonic
    df = df.reindex([df.index[2], df.index[0], df.index[1]])  # Order: 2024-01-05, 2024-01-03, 2024-01-04
    errors = validate_market_data(df)
    assert any("monotonically increasing" in e for e in errors)

def test_validate_market_data_illogical_prices():
    """Test validation of illogical price relationships (High < Low, etc)."""
    df = pd.DataFrame({
        "Open": [10.0],
        "High": [9.0],   # High < Low (we'll set Low to 10)
        "Low": [10.0],
        "Close": [10.0],
        "Volume": [100]
    }, index=pd.date_range("2024-01-01", periods=1))
    errors = validate_market_data(df)
    assert any("High < Low" in e for e in errors)

    # High < Open
    df = pd.DataFrame({
        "Open": [10.0],
        "High": [9.0],
        "Low": [8.0],
        "Close": [9.0],
        "Volume": [100]
    }, index=pd.date_range("2024-01-01", periods=1))
    errors = validate_market_data(df)
    assert any("High < Open" in e for e in errors)

    # High < Close
    df = pd.DataFrame({
        "Open": [10.0],
        "High": [9.0],
        "Low": [8.0],
        "Close": [9.5],
        "Volume": [100]
    }, index=pd.date_range("2024-01-01", periods=1))
    errors = validate_market_data(df)
    assert any("High < Close" in e for e in errors)

    # Low > Open
    df = pd.DataFrame({
        "Open": [10.0],
        "High": [12.0],
        "Low": [11.0],   # Low > Open
        "Close": [11.0],
        "Volume": [100]
    }, index=pd.date_range("2024-01-01", periods=1))
    errors = validate_market_data(df)
    assert any("Low > Open" in e for e in errors)

    # Low > Close
    df = pd.DataFrame({
        "Open": [10.0],
        "High": [12.0],
        "Low": [11.0],   # Low > Close
        "Close": [10.5],
        "Volume": [100]
    }, index=pd.date_range("2024-01-01", periods=1))
    errors = validate_market_data(df)
    assert any("Low > Close" in e for e in errors)

def test_validate_market_data_missing_values():
    """Test validation of missing values (NaN)."""
    df = pd.DataFrame({
        "Open": [1.0, None, 3.0],
        "High": [2.0, 3.0, 4.0],
        "Low": [0.5, 1.5, 2.5],
        "Close": [1.5, 2.5, 3.5],
        "Volume": [100, 200, 300]
    }, index=pd.date_range("2024-01-01", periods=3))
    errors = validate_market_data(df)
    assert any("Open" in e and "missing" in e for e in errors)
