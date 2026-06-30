import pandas as pd
import numpy as np
from typing import Callable, Dict

def price_above_min(feature_matrix: pd.DataFrame, min_price: float = 10.0, price_col: str = 'Close') -> pd.Series:
    """
    Filter: price above a minimum threshold.
    Assumes feature_matrix has a column named price_col (default 'Close').
    Returns a boolean Series indexed by asset.
    """
    if price_col not in feature_matrix.columns:
        return pd.Series(False, index=feature_matrix.index)
    return feature_matrix[price_col] > min_price

def volume_above_min(feature_matrix: pd.DataFrame, min_volume: float = 500000.0, volume_col: str = 'Volume') -> pd.Series:
    """
    Filter: volume above a minimum threshold.
    Assumes a column named volume_col (default 'Volume').
    Returns a boolean Series indexed by asset.
    """
    if volume_col not in feature_matrix.columns:
        return pd.Series(False, index=feature_matrix.index)
    return feature_matrix[volume_col] > min_volume

def above_200_ma(feature_matrix: pd.DataFrame, price_col: str = 'Close', ma_col: str = 'sma_200') -> pd.Series:
    """
    Filter: price above its 200-day moving average.
    Assumes we have columns for price and the 200-day moving average.
    Returns a boolean Series indexed by asset.
    """
    if price_col not in feature_matrix.columns or ma_col not in feature_matrix.columns:
        return pd.Series(False, index=feature_matrix.index)
    return feature_matrix[price_col] > feature_matrix[ma_col]

def volatility_below_max(feature_matrix: pd.DataFrame, max_volatility: float = 0.5, vol_col: str = None) -> pd.Series:
    """
    Filter: volatility below a maximum.
    If vol_col is provided, use that column; otherwise, try to auto-detect a volatility column.
    Returns a boolean Series indexed by asset.
    """
    if vol_col is None:
        # Try to find a column that looks like volatility
        vol_candidates = [c for c in feature_matrix.columns if 'volatility' in c.lower() or 'atr' in c.lower()]
        if not vol_candidates:
            return pd.Series(False, index=feature_matrix.index)
        vol_col = vol_candidates[0]
    if vol_col not in feature_matrix.columns:
        return pd.Series(False, index=feature_matrix.index)
    return feature_matrix[vol_col] < max_volatility

# Dictionary mapping filter names to functions
FILTER_FUNCTIONS: Dict[str, Callable] = {
    'price_above_min': price_above_min,
    'volume_above_min': volume_above_min,
    'above_200_ma': above_200_ma,
    'volatility_below_max': volatility_below_max,
}

def get_filter_function(name: str) -> Callable:
    """
    Retrieve a filter function by name.
    """
    return FILTER_FUNCTIONS[name]
