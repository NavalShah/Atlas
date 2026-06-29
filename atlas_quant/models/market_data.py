"""Market data models."""

import pandas as pd
from typing import Optional
from loguru import logger


class MarketData:
    """Container for market data with utility methods."""

    def __init__(self, data: pd.DataFrame, ticker: str = None):
        """Initialize with OHLCV data.

        Args:
            data: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume'] and
                  datetime index.
            ticker: Optional ticker symbol.
        """
        self.data = data
        self.ticker = ticker
        logger.debug(f"Created MarketData for {ticker} with {len(data)} rows")

    @property
    def open(self) -> pd.Series:
        """Open prices."""
        return self.data["Open"]

    @property
    def high(self) -> pd.Series:
        """High prices."""
        return self.data["High"]

    @property
    def low(self) -> pd.Series:
        """Low prices."""
        return self.data["Low"]

    @property
    def close(self) -> pd.Series:
        """Close prices."""
        return self.data["Close"]

    @property
    def volume(self) -> pd.Series:
        """Volume."""
        return self.data["Volume"]

    @property
    def date_range(self) -> tuple:
        """Return (min_date, max_date) as Timestamps."""
        if self.data.empty:
            return (None, None)
        return (self.data.index.min(), self.data.index.max())

    def to_dict(self) -> dict:
        """Convert to dictionary (for serialization)."""
        return {
            "ticker": self.ticker,
            "data": self.data.to_dict()
        }

    @classmethod
    def from_dict(cls, data_dict: dict):
        """Create from dictionary."""
        data = pd.DataFrame(data_dict["data"])
        # Convert index back to datetime if needed
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        return cls(data, ticker=data_dict.get("ticker"))

    def __repr__(self):
        return f"MarketData(ticker={self.ticker}, rows={len(self.data)})"
