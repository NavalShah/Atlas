import pytest
import pandas as pd
from unittest.mock import patch
from atlas_quant.data.manager import MarketDataManager
from atlas_quant.exceptions import DownloadError, ValidationError, CacheError, ConfigurationError
import yaml
import os
from pathlib import Path

# Sample data to return when mocking
SAMPLE_DATA = pd.DataFrame({
    "Open": [1.0, 2.0, 3.0],
    "High": [2.0, 3.0, 4.0],
    "Low": [0.5, 1.5, 2.5],
    "Close": [1.5, 2.5, 3.5],
    "Volume": [100, 200, 300]
}, index=pd.date_range("2024-01-01", periods=3))

def test_manager_initialization_default(tmp_path):
    """Test manager initialization with default config (using a temporary config file)."""
    # Create a temporary config file with default values
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "settings.yaml"
    config_data = {
        "data_provider": "yahoo",
        "cache_directory": "data/cache",
        "default_start_date": "2010-01-01",
        "auto_update": True,
        "retry_attempts": 3,
        "retry_delay_seconds": 5,
        "log_level": "INFO"
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)
    
    manager = MarketDataManager(config_path=config_file)
    assert manager.cache_dir == Path("data/cache")
    assert manager.data_provider == "yahoo"
    assert manager.default_start_date == "2010-01-01"

def test_manager_initialization_custom_config(tmp_path):
    """Test manager initialization with a custom config file."""
    config_file = tmp_path / "test_config.yaml"
    config_data = {
        "data_provider": "yahoo",
        "cache_directory": "test_cache",
        "default_start_date": "2020-01-01",
        "auto_update": False,
        "retry_attempts": 5,
        "retry_delay_seconds": 10,
        "log_level": "DEBUG"
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    manager = MarketDataManager(config_path=config_file)
    assert manager.cache_dir == Path("test_cache")
    assert manager.data_provider == "yahoo"
    assert manager.default_start_date == "2020-01-01"
    assert manager.auto_update == False
    assert manager.retry_attempts == 5
    assert manager.retry_delay_seconds == 10
    assert manager.log_level == "DEBUG"

def test_manager_load_config_file_not_found():
    """Test that loading a non-existent config file raises ConfigurationError."""
    with pytest.raises(ConfigurationError):
        MarketDataManager(config_path="non_existent.yaml")

def test_get_data_cache_miss(tmp_path):
    """Test getting data when cache is missing (should download and cache)."""
    # We use a temporary directory for cache
    cache_dir = tmp_path / "cache"
    # Create a manager with the temporary cache directory
    # We need to create a config object, but we can override the cache directory after initialization
    # Alternatively, create a custom config file.
    config_file = tmp_path / "test_config.yaml"
    config_data = {
        "data_provider": "yahoo",
        "cache_directory": str(cache_dir),
        "default_start_date": "2024-01-01",
        "auto_update": True,
        "retry_attempts": 3,
        "retry_delay_seconds": 1,
        "log_level": "INFO"
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    manager = MarketDataManager(config_path=config_file)

    # Use a very short period and a reliable ticker
    ticker = "MSFT"
    start = "2024-01-01"
    end = "2024-01-02"

    # Mock the download_data function to return our sample data
    with patch("atlas_quant.data.manager.download_data") as mock_download:
        mock_download.return_value = SAMPLE_DATA
        # This will download data (if network is available) and cache it
        data = manager.get_data(ticker=ticker, start=start, end=end)

    # Check that we got data
    assert not data.empty
    assert "Open" in data.columns
    assert "Close" in data.columns
    # Check that the cache was created
    cache_file = cache_dir / f"{ticker}.csv"
    assert cache_file.exists()

def test_get_data_cache_hit(tmp_path):
    """Test getting data when cache exists and is up-to-date."""
    cache_dir = tmp_path / "cache"
    config_file = tmp_path / "test_config.yaml"
    config_data = {
        "data_provider": "yahoo",
        "cache_directory": str(cache_dir),
        "default_start_date": "2020-01-01",
        "auto_update": True,
        "retry_attempts": 3,
        "retry_delay_seconds": 1,
        "log_level": "INFO"
    }
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    manager = MarketDataManager(config_path=config_file)

    ticker = "MSFT"
    # First, we need to populate the cache by calling get_data once
    with patch("atlas_quant.data.manager.download_data") as mock_download:
        mock_download.return_value = SAMPLE_DATA
        data_first = manager.get_data(ticker=ticker, start="2024-01-01", end="2024-01-02")
    # Now, call again for the same range - should hit cache
    data_second = manager.get_data(ticker=ticker, start="2024-01-01", end="2024-01-02")

    # The data should be the same
    assert data_first.equals(data_second)

# The following function is not a test because it doesn't start with "test_"
# def get_data_multiple(tmp_path):
#     """Test getting data for multiple tickers."""
#     cache_dir = tmp_path / "cache"
#     config_file = tmp_path / "test_config.yaml"
#     config_data = {
#         "data_provider": "yahoo",
#         "cache_directory": str(cache_dir),
#         "default_start_date": "2020-01-01",
#         "auto_update": True,
#         "retry_attempts": 3
#     }
#     with open(config_file, "w") as f:
#         yaml.dump(config_data, f)
#
#     manager = MarketDataManager(config_path=config_file)
#
#     ts = ["MSFT", "AAPL"]
#     data = manager.get_multiple_data(tickers=ts, start="2024-01-01", end="2024-01-02")
#
#     assert isinstance(data, dict)
#     assert "MSFT" in data
#     assert "AAPL" in data
#     assert not data["MSFT"].empty
#     assert not data["AAPL"].empty
