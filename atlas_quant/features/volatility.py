"""Volatility-based technical indicators."""

import pandas as pd
import numpy as np
from typing import List
from .base import BaseFeature


class ATR(BaseFeature):
    """Average True Range (ATR).

    The ATR measures market volatility by decomposing the entire range of an asset price for that period.

    Formula:
        TR = max[(High - Low), abs(High - Close_prev), abs(Low - Close_prev)]
        ATR = MA(TR, period)

    Args:
        period: The lookback period (default: 14).
    """

    feature_key = 'atr'

    def __init__(self, period: int = 14):
        self.period = period
        self._name = f'atr_{self.period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'volatility'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return ['High', 'Low', 'Close']

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period:
            raise ValueError(f"Insufficient data: need at least {self.period} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # True Range
        high_low = df['High'] - df['Low']
        high_close_prev = np.abs(df['High'] - df['Close'].shift(1))
        low_close_prev = np.abs(df['Low'] - df['Close'].shift(1))
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = tr.rolling(window=self.period).mean()
        df[self.name] = atr
        return df


class HistoricalVolatility(BaseFeature):
    """Historical Volatility.

    The historical volatility is the standard deviation of logarithmic returns over a given period.

    Formula:
        HV = std(log(Close_t / Close_{t-1})) * sqrt(period)  # often annualized, but we output raw

    Args:
        period: The lookback period (default: 20).
    """

    feature_key = 'historical_volatility'

    def __init__(self, period: int = 20):
        self.period = period
        self._name = f'historical_volatility_{self.period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'volatility'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return ['Close']

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period + 1:
            raise ValueError(f"Insufficient data: need at least {self.period + 1} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Log returns
        log_returns = np.log(df['Close'] / df['Close'].shift(1))
        # Rolling standard deviation
        vol = log_returns.rolling(window=self.period).std()
        df[self.name] = vol
        return df


class BollingerBands(BaseFeature):
    """Bollinger Bands.

    Bollinger Bands consist of a middle band (SMA) and two outer bands that are standard deviations away from the middle band.

    Formula:
        MIDDLE = SMA(Close, period)
        UPPER = MIDDLE + (std_dev * std(Close, period))
        LOWER = MIDDLE - (std_dev * std(Close, period))

    Args:
        period: The lookback period for the middle band (default: 20).
        std_dev: The number of standard deviations for the outer bands (default: 2).
        column: The column to use for calculations (default: 'Close').
    """

    feature_key = 'bollingerbands'

    def __init__(self, period: int = 20, std_dev: int = 2, column: str = 'Close'):
        self.period = period
        self.std_dev = std_dev
        self.column = column
        self._name = f'bollingerbands_{self.period}_{self.std_dev}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'volatility'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.column]

    @property
    def generated_columns(self) -> List[str]:
        return [
            f'{self.name}_middle',
            f'{self.name}_upper',
            f'{self.name}_lower'
        ]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period:
            raise ValueError(f"Insufficient data: need at least {self.period} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Middle band
        middle = df[self.column].rolling(window=self.period).mean()
        # Standard deviation
        std_dev = df[self.column].rolling(window=self.period).std()
        # Upper and lower bands
        upper = middle + (self.std_dev * std_dev)
        lower = middle - (self.std_dev * std_dev)
        df[f'{self.name}_middle'] = middle
        df[f'{self.name}_upper'] = upper
        df[f'{self.name}_lower'] = lower
        return df