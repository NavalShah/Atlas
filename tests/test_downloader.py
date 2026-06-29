import pytest
import pandas as pd
from unittest.mock import patch
from atlas_quant.data.downloader import download_data, download_multiple_tickers
from atlas_quant.exceptions import DownloadError

# Sample data to return when mocking
SAMPLE_DATA = pd.DataFrame({
    "Open": [1.0, 2.0, 3.0],
    "High": [2.0, 3.0, 4.0],
    "Low": [0.5, 1.5, 2.5],
    "Close": [1.5, 2.5, 3.5],
    "Volume": [100, 200, 300]
}, index=pd.date_range("2024-01-01", periods=3))

def test_download_data_valid_ticker():
    """Test downloading data for a valid ticker."""
    with patch("atlas_quant.data.downloader.yf.download") as mock_download:
        mock_download.return_value = SAMPLE_DATA
        data = download_data("AAPL", "2024-01-01", "2024-01-31")
        assert not data.empty
        assert "Open" in data.columns
        assert "High" in data.columns
        assert "Low" in data.columns
        assert "Close" in data.columns
        assert "Volume" in data.columns
        # Verify the download was called with the correct arguments
        mock_download.assert_called_once_with("AAPL", start="2024-01-01", end="2024-01-31", interval="1d")

def test_download_data_invalid_ticker():
    """Test downloading data for an invalid ticker raises DownloadError."""
    # For an invalid ticker, we want the download to return an empty DataFrame
    with patch("atlas_quant.data.downloader.yf.download") as mock_download:
        mock_download.return_value = pd.DataFrame()  # Empty DataFrame
        with pytest.raises(DownloadError):
            download_data("INVALIDTICKER123", "2024-01-01", "2024-01-31")

def test_download_multiple_tickers():
    """Test downloading data for multiple tickers."""
    with patch("atlas_quant.data.downloader.yf.download") as mock_download:
        mock_download.return_value = SAMPLE_DATA
        tickers = ["AAPL", "MSFT"]
        data = download_multiple_tickers(tickers, "2024-01-01", "2024-01-31")
        assert isinstance(data, dict)
        assert "AAPL" in data
        assert "MSFT" in data
        assert not data["AAPL"].empty
        assert not data["MSFT"].empty
        # Should have been called twice
        assert mock_download.call_count == 2

def test_download_multiple_tickers_with_invalid():
    """Test downloading multiple tickers with one invalid raises DownloadError."""
    def download_side_effect(ticker, start, end, interval):
        if ticker == "INVALIDTICKER123":
            return pd.DataFrame()  # Empty DataFrame for invalid ticker
        return SAMPLE_DATA

    with patch("atlas_quant.data.downloader.yf.download") as mock_download:
        mock_download.side_effect = download_side_effect
        tickers = ["AAPL", "INVALIDTICKER123"]
        with pytest.raises(DownloadError):
            download_multiple_tickers(tickers, "2024-01-01", "2024-01-31")
