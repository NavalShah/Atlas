import pandas as pd
import numpy as np
from typing import Callable, Dict

def raw_feature_signal(feature_matrix: pd.DataFrame, feature_name: str) -> pd.Series:
    """
    Signal: returns the raw feature value.
    Assumes the feature is already scaled appropriately (e.g., RSI 0-100).
    If the feature is not present, returns zeros.
    """
    if feature_name not in feature_matrix.columns:
        return pd.Series(0.0, index=feature_matrix.index)
    return feature_matrix[feature_name]

def momentum_signal(feature_matrix: pd.DataFrame) -> pd.Series:
    """
    Example momentum signal: use RSI (0-100) or ROC.
    We'll look for a column with 'rsi' or 'roc' in the name.
    If multiple, we'll use the first.
    """
    mom_cols = [col for col in feature_matrix.columns if 'rsi' in col.lower() or 'roc' in col.lower()]
    if not mom_cols:
        return pd.Series(0.0, index=feature_matrix.index)
    # Use the first momentum column
    return feature_matrix[mom_cols[0]]

def trend_signal(feature_matrix: pd.DataFrame, price_col: str = 'Close', ma_col: str = 'sma_50') -> pd.Series:
    """
    Example trend signal: price above moving average, normalized to 0-100.
    We'll compute: if price > ma -> 100, else 0 (binary). Could also be continuous.
    Returns a Series indexed by asset.
    """
    if price_col not in feature_matrix.columns or ma_col not in feature_matrix.columns:
        return pd.Series(50.0, index=feature_matrix.index)  # neutral
    # Binary: 100 if above, 0 if below
    return np.where(feature_matrix[price_col] > feature_matrix[ma_col], 100.0, 0.0)

def relative_strength_signal(feature_matrix: pd.DataFrame) -> pd.Series:
    """
    Example relative strength: ratio of stock price to benchmark price.
    Assumes we have a column like 'relative_strength_spy' (from market features).
    Returns a Series indexed by asset.
    """
    rs_cols = [col for col in feature_matrix.columns if 'relative_strength' in col.lower()]
    if not rs_cols:
        return pd.Series(50.0, index=feature_matrix.index)
    # Assume the ratio is already computed; we need to map to 0-100.
    # For simplicity, we'll just return the value if it's already 0-100, else we'll normalize.
    # We'll just return the value as is, assuming it's already a score.
    return feature_matrix[rs_cols[0]]

def volume_signal(feature_matrix: pd.DataFrame, volume_col: str = 'Volume', avg_volume_col: str = None) -> pd.Series:
    """
    Example volume signal: relative volume (volume / average volume).
    If avg_volume_col is provided, use that; otherwise, try to compute from a column like 'volume_sma_20'.
    Returns a Series indexed by asset.
    """
    if volume_col not in feature_matrix.columns:
        return pd.Series(50.0, index=feature_matrix.index)
    if avg_volume_col is None:
        # Look for a column that looks like average volume
        avg_vol_candidates = [c for c in feature_matrix.columns if 'volume' in c.lower() and 'sma' in c.lower()]
        if not avg_vol_candidates:
            return pd.Series(50.0, index=feature_matrix.index)
        avg_volume_col = avg_vol_candidates[0]
    if avg_volume_col not in feature_matrix.columns:
        return pd.Series(50.0, index=feature_matrix.index)
    # Avoid division by zero
    rel_vol = feature_matrix[volume_col] / feature_matrix[avg_volume_col].replace(0, np.nan)
    # We'll clip to reasonable range and scale to 0-100? For simplicity, we'll just return the ratio * 50? 
    # Actually, we want a score where higher relative volume -> higher score.
    # We'll clamp the ratio to [0, 3] and map to [0,100]: (ratio/3)*100, but cap at 100.
    # Let's do: score = min(rel_vol, 3) / 3 * 100
    scaled = np.minimum(rel_vol, 3.0) / 3.0 * 100.0
    return pd.Series(scaled, index=feature_matrix.index)

def volatility_signal(feature_matrix: pd.DataFrame, vol_col: str = None) -> pd.Series:
    """
    Example volatility signal: inverse of volatility (so lower volatility -> higher score).
    We'll compute: 100 * (1 - (vol - min_vol) / (max_vol - min_vol)) but we don't have min/max.
    Instead, we'll use the negative of the volatility and then rank across assets? That would be cross-sectional.
    For simplicity, we'll assume the volatility column is already a score (0-100) where lower is better? 
    Actually, we want higher score for lower volatility.
    We'll do: if we have a volatility column, we'll compute: 100 - volatility (if volatility is already 0-100).
    If not, we'll just return 50.
    Returns a Series indexed by asset.
    """
    if vol_col is None:
        vol_candidates = [c for c in feature_matrix.columns if 'volatility' in c.lower() or 'atr' in c.lower()]
        if not vol_candidates:
            return pd.Series(50.0, index=feature_matrix.index)
        vol_col = vol_candidates[0]
    if vol_col not in feature_matrix.columns:
        return pd.Series(50.0, index=feature_matrix.index)
    # Assume volatility is already a positive number; we'll invert and scale to 0-100.
    # We'll do a simple inversion: max_vol - vol, but we don't know max.
    # Instead, we'll rank the volatility ascending and assign scores based on rank.
    # But that would be cross-sectional and dependent on the cohort.
    # For simplicity, we'll just return 100 - volatility (if volatility is between 0 and 100).
    # We'll check if the values look like they are in 0-100 range.
    vol_series = feature_matrix[vol_col]
    if (vol_series >= 0).all() and (vol_series <= 100).all():
        return 100.0 - vol_series
    else:
        # Fallback: just return the negative (so higher volatility gives lower score) but not bounded.
        return -vol_series

SIGNAL_FUNCTIONS = {
    'momentum': momentum_signal,
    'trend': trend_signal,
    'relative_strength': relative_strength_signal,
    'volume': volume_signal,
    'volatility': volatility_signal,
}

SIGNAL_FUNCTIONS = {
    'momentum': momentum_signal,
    'trend': trend_signal,
    'relative_strength': relative_strength_signal,
    'volume': volume_signal,
    'volatility': volatility_signal,
}
