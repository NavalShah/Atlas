import pytest
import pandas as pd
from atlas_quant.data.cache import save_data, load_cached_data, cache_exists, get_cached_date_range, update_cache
from pathlib import Path
import tempfile
import os

def test_cache_save_and_load():
    """Test saving and loading cached data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ticker = "TEST"
        df = pd.DataFrame({
            "Open": [1.0, 2.0, 3.0],
            "High": [2.0, 3.0, 4.0],
            "Low": [0.5, 1.5, 2.5],
            "Close": [1.5, 2.5, 3.5],
            "Volume": [100, 200, 300]
        }, index=pd.date_range("2024-01-01", periods=3))

        # Save data
        save_data(ticker, df, tmpdir)

        # Check that cache exists
        assert cache_exists(ticker, tmpdir)

        # Load data
        df_loaded = load_cached_data(ticker, tmpdir)
        assert not df_loaded.empty
        # Check that the data is the same (ignoring index name and frequency)
        pd.testing.assert_frame_equal(df, df_loaded, check_names=False, check_freq=False)

def test_cache_no_file():
    """Test loading from non-existent cache returns empty DataFrame."""
    with tempfile.TemporaryDirectory() as tmpdir:
        df = load_cached_data("NONEXISTENT", tmpdir)
        assert df.empty

def test_get_cached_date_range():
    """Test getting date range from cached data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ticker = "TEST"
        df = pd.DataFrame({
            "Open": [1.0, 2.0, 3.0],
            "High": [2.0, 3.0, 4.0],
            "Low": [0.5, 1.5, 2.5],
            "Close": [1.5, 2.5, 3.5],
            "Volume": [100, 200, 300]
        }, index=pd.date_range("2024-01-01", periods=3))

        save_data(ticker, df, tmpdir)

        min_date, max_date = get_cached_date_range(ticker, tmpdir)
        assert min_date == pd.Timestamp("2024-01-01")
        assert max_date == pd.Timestamp("2024-01-03")

def test_get_cached_date_range_no_file():
    """Test getting date range when no cache exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        min_date, max_date = get_cached_date_range("NONEXISTENT", tmpdir)
        assert min_date is None
        assert max_date is None

def test_update_cache():
    """Test updating cache with new data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ticker = "TEST"
        # Initial data
        df1 = pd.DataFrame({
            "Open": [1.0, 2.0],
            "High": [2.0, 3.0],
            "Low": [0.5, 1.5],
            "Close": [1.5, 2.5],
            "Volume": [100, 200]
        }, index=pd.date_range("2024-01-01", periods=2))

        # New data (overlapping and new)
        df2 = pd.DataFrame({
            "Open": [2.5, 3.0],
            "High": [3.5, 4.0],
            "Low": [1.5, 2.0],
            "Close": [2.5, 3.0],
            "Volume": [250, 300]
        }, index=pd.date_range("2024-01-02", periods=2))  # Overlaps on 2024-01-02

        # Save initial data
        save_data(ticker, df1, tmpdir)

        # Update cache
        updated = update_cache(ticker, df2, tmpdir)

        # Check that updated data has the correct rows
        # We expect three rows: 2024-01-01 from df1, 2024-01-02 from df2 (duplicate kept last), 2024-01-03 from df2
        assert len(updated) == 3
        # Check that the values for 2024-01-02 are from df2 (the later one)
        assert updated.loc["2024-01-02", "Open"] == 2.5
        assert updated.loc["2024-01-02", "Close"] == 2.5
        # Check that the date range is correct
        assert updated.index.min() == pd.Timestamp("2024-01-01")
        assert updated.index.max() == pd.Timestamp("2024-01-03")

def test_update_cache_no_existing():
    """Test updating cache when no existing cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        ticker = "TEST"
        df = pd.DataFrame({
            "Open": [1.0, 2.0],
            "High": [2.0, 3.0],
            "Low": [0.5, 1.5],
            "Close": [1.5, 2.5],
            "Volume": [100, 200]
        }, index=pd.date_range("2024-01-01", periods=2))

        updated = update_cache(ticker, df, tmpdir)
        # Should just save the data
        assert not updated.empty
        assert len(updated) == 2
        # Check that cache exists
        assert cache_exists(ticker, tmpdir)
