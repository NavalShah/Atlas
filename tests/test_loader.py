import pytest
import pandas as pd
from atlas_quant.data.loader import load_cached_ticker, load_csv
from pathlib import Path
import tempfile
import os

def test_load_cached_ticker_no_file():
    """Test loading cached ticker when file does not exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        df = load_cached_ticker("NONEXISTENT", tmpdir)
        assert df.empty

def test_load_csv():
    """Test loading a CSV file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        # Create a sample CSV
        df_expected = pd.DataFrame({
            "Open": [1, 2, 3],
            "High": [1, 2, 3],
            "Low": [1, 2, 3],
            "Close": [1, 2, 3],
            "Volume": [100, 200, 300]
        }, index=pd.date_range("2024-01-01", periods=3))
        df_expected.index.name = "Date"
        df_expected.to_csv(csv_path)

        df_loaded = load_csv(csv_path)
        # Check that the data is loaded correctly
        assert not df_loaded.empty
        assert "Open" in df_loaded.columns
        assert "High" in df_loaded.columns
        assert "Low" in df_loaded.columns
        assert "Close" in df_loaded.columns
        assert "Volume" in df_loaded.columns
        # Check that the index is a DatetimeIndex
        assert isinstance(df_loaded.index, pd.DatetimeIndex)
        # Check a few values
        assert df_loaded.loc["2024-01-01", "Open"] == 1
        assert df_loaded.loc["2024-01-02", "Close"] == 2

def test_load_csv_file_not_found():
    """Test loading a non-existent CSV file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_csv("non_existent_file.csv")
