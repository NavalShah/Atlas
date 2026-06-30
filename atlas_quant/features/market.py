"""Market-based technical indicators."""

import pandas as pd
import numpy as np
from typing import List
from .base import BaseFeature


class RelativeStrength(BaseFeature):
    """Relative Strength.

    The relative strength is the ratio of the asset's price to the benchmark's price.

    Formula:
        RS = Asset_Close / Benchmark_Close

    Args:
        asset_column: The column to use for asset price (default: 'Close').
        benchmark_column: The column to use for benchmark price (default: 'SPY_Close').
    """

    feature_key = 'relative_strength'

    def __init__(self, asset_column: str = 'Close', benchmark_column: str = 'SPY_Close'):
        self.asset_column = asset_column
        self.benchmark_column = benchmark_column
        self._name = f'relative_strength_{self.benchmark_column.split("_")[0].lower()}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'market'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.asset_column, self.benchmark_column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < 1:
            raise ValueError("Insufficient data: need at least 1 row to compute relative strength")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        df[self.name] = df[self.asset_column] / df[self.benchmark_column]
        return df


class Beta(BaseFeature):
    """Beta.

    Beta measures the sensitivity of the asset's returns to the benchmark's returns.

    Formula:
        β = Cov(R_asset, R_benchmark) / Var(R_benchmark)

    where R_asset and R_benchmark are simple returns.

    Args:
        asset_column: The column to use for asset price (default: 'Close').
        benchmark_column: The column for benchmark price (default: 'SPY_Close').
        window: The lookback window for beta calculation (default: 252 trading days).
    """

    feature_key = 'beta'

    def __init__(self, asset_column: str = 'Close', benchmark_column: str = 'SPY_Close', window: int = 252):
        self.asset_column = asset_column
        self.benchmark_column = benchmark_column
        self.window = window
        self._name = f'beta_{self.benchmark_column.split("_")[0].lower()}_{self.window}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'market'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.asset_column, self.benchmark_column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < 2:
            raise ValueError("Insufficient data: need at least 2 rows to compute returns")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Calculate simple returns
        asset_ret = df[self.asset_column].pct_change()
        bench_ret = df[self.benchmark_column].pct_change()
        # Calculate beta using rolling covariance and variance
        cov = asset_ret.rolling(window=self.window).cov(bench_ret)
        var = bench_ret.rolling(window=self.window).var()
        df[self.name] = cov / var
        return df


class RollingCorrelation(BaseFeature):
    """Rolling Correlation.

    The rolling correlation between the asset's returns and the benchmark's returns.

    Args:
        asset_column: The column to use for asset price (default: 'Close').
        benchmark_column: The column for benchmark price (default: 'SPY_Close').
        window: The lookback window for correlation (default: 252 trading days).
    """

    feature_key = 'rollingcorrelation'

    def __init__(self, asset_column: str = 'Close', benchmark_column: str = 'SPY_Close', window: int = 252):
        self.asset_column = asset_column
        self.benchmark_column = benchmark_column
        self.window = window
        self._name = f'rolling_corr_{self.benchmark_column.split("_")[0].lower()}_{self.window}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'market'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.asset_column, self.benchmark_column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < 2:
            raise ValueError("Insufficient data: need at least 2 rows to compute returns")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Calculate simple returns
        asset_ret = df[self.asset_column].pct_change()
        bench_ret = df[self.benchmark_column].pct_change()
        # Calculate rolling correlation
        df[self.name] = asset_ret.rolling(window=self.window).corr(bench_ret)
        return df


class ExcessReturn(BaseFeature):
    """Excess Return.

    The excess return is the asset's return minus the benchmark's return.

    Formula:
        Excess Return = R_asset - R_benchmark

    Args:
        asset_column: The column to use for asset price (default: 'Close').
        benchmark_column: The column for benchmark price (default: 'SPY_Close').
    """

    feature_key = 'excessreturn'

    def __init__(self, asset_column: str = 'Close', benchmark_column: str = 'SPY_Close'):
        self.asset_column = asset_column
        self.benchmark_column = benchmark_column
        self._name = f'excess_return_{self.benchmark_column.split("_")[0].lower()}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'market'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.asset_column, self.benchmark_column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < 2:
            raise ValueError("Insufficient data: need at least 2 rows to compute returns")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Calculate simple returns
        asset_ret = df[self.asset_column].pct_change()
        bench_ret = df[self.benchmark_column].pct_change()
        df[self.name] = asset_ret - bench_ret
        return df


class TrackingError(BaseFeature):
    """Tracking Error.

    The tracking error is the standard deviation of the excess returns.

    Formula:
        Tracking Error = std(R_asset - R_benchmark)

    Typically annualized, but we leave it as is for simplicity.

    Args:
        asset_column: The column to use for asset price (default: 'Close').
        benchmark_column: The column for benchmark price (default: 'SPY_Close').
        window: The lookback window for tracking error (default: 252 trading days).
    """

    feature_key = 'trackingerror'

    def __init__(self, asset_column: str = 'Close', benchmark_column: str = 'SPY_Close', window: int = 252):
        self.asset_column = asset_column
        self.benchmark_column = benchmark_column
        self.window = window
        self._name = f'tracking_error_{self.benchmark_column.split("_")[0].lower()}_{self.window}'

    @property
    def name(self) -> str:
        return self._name

    _category = 'market'
    @property
    def category(self) -> str:
        return self._category

    @property
    def required_columns(self) -> List[str]:
        return [self.asset_column, self.benchmark_column]

    @property
    def generated_columns(self) -> List[str]:
        return [self.name]

    def validate(self, dataframe: pd.DataFrame) -> None:
        super().validate(dataframe)
        if len(dataframe) < 2:
            raise ValueError("Insufficient data: need at least 2 rows to compute returns")

    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        # Calculate simple returns
        asset_ret = df[self.asset_column].pct_change()
        bench_ret = df[self.benchmark_column].pct_change()
        excess_ret = asset_ret - bench_ret
        # Calculate rolling standard deviation of excess returns
        df[self.name] = excess_ret.rolling(window=self.window).std()
        return df