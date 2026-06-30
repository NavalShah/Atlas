"""Momentum-based technical indicators."""

import pandas as pd
import numpy as np
from typing import List
from .base import BaseFeature


class RSI(BaseFeature):
    """Relative Strength Index (RSI).

    The RSI measures the speed and change of price movements.

    Formula:
        RS = Average Gain / Average Loss
        RSI = 100 - (100 / (1 + RS))

    Args:
        period: The lookback period for the average gain and loss (default: 14).
        column: The column to use for calculations (default: 'Close').
    """

    feature_key = 'rsi'

    def __init__(self, period: int = 14, column: str = 'Close'):
        self.period = period
        self.column = column
        self._name = f'rsi_{self.period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'momentum'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period + 1:  # Need at least period+1 for the first RS
            raise ValueError(f"Insufficient data: need at least {self.period + 1} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Calculate price changes
        delta = df[self.column].diff()
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        # Calculate average gain and loss over the period
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        # Calculate RS
        rs = avg_gain / avg_loss.replace(0, np.nan)
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        df[self.name] = rsi
        return df


class ROC(BaseFeature):
    """Rate of Change (ROC).

    The ROC measures the percentage change in price over a specified period.

    Formula:
        ROC = (Close_t - Close_{t-n}) / Close_{t-n} * 100

    Args:
        period: The lookback period (default: 12).
        column: The column to use for calculations (default: 'Close').
    """

    feature_key = 'roc'

    def __init__(self, period: int = 12, column: str = 'Close'):
        self.period = period
        self.column = column
        self._name = f'roc_{self.period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'momentum'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period + 1:
            raise ValueError(f"Insufficient data: need at least {self.period + 1} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        roc = (df[self.column] - df[self.column].shift(self.period)) / df[self.column].shift(self.period)
        df[self.name] = roc * 100
        return df


class Momentum(BaseFeature):
    """Momentum.

    The momentum indicator measures the difference between the current price and the price n periods ago.

    Formula:
        Momentum = Close_t - Close_{t-n}

    Args:
        period: The lookback period (default: 10).
        column: The column to use for calculations (default: 'Close').
    """

    feature_key = 'momentum'

    def __init__(self, period: int = 10, column: str = 'Close'):
        self.period = period
        self.column = column
        self._name = f'momentum_{self.period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'momentum'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.period + 1:
            raise ValueError(f"Insufficient data: need at least {self.period + 1} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        mom = df[self.column] - df[self.column].shift(self.period)
        df[self.name] = mom
        return df


class StochasticOscillator(BaseFeature):
    """Stochastic Oscillator.

    The stochastic oscillator compares the closing price to the price range over a given period.

    Formula:
        %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
        %D = SMA of %K over the signal period

    Args:
        k_period: The lookback period for %K (default: 14).
        d_period: The smoothing period for %D (default: 3).
        column: The column to use for calculations (default: 'Close').
    """

    feature_key = 'stochastic'

    def __init__(self, k_period: int = 14, d_period: int = 3, column: str = 'Close'):
        self.k_period = k_period
        self.d_period = d_period
        self.column = column
        self._name = f'stochastic_{self.k_period}_{self.d_period}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'momentum'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return ['High', 'Low', 'Close']

    @property
    def generated_columns(self) -> List[str]:
        return [f'{self.name}_k', f'{self.name}_d']

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < self.k_period:
            raise ValueError(f"Insufficient data: need at least {self.k_period} rows, got {len(dataframe)}")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        lowest_low = df['Low'].rolling(window=self.k_period).min()
        highest_high = df['High'].rolling(window=self.k_period).max()
        k = (df['Close'] - lowest_low) / (highest_high - lowest_low) * 100
        d = k.rolling(window=self.d_period).mean()
        df[f'{self.name}_k'] = k
        df[f'{self.name}_d'] = d
        return df